
from common.model               import reload_object
from common.test                import TestAPIWithLogin

from django.utils               import timezone

from mock                       import patch

from planning_mgr.models        import MetaPlanning

from user_mgr.models            import ConfigStageCompletion

import datetime

import planning_mgr.controller.meta

class TestConfigStages(TestAPIWithLogin):
    """
    Test the API to complete configuration stages
    """
    def setUp(self):
        super().setUp()

        self.stage1 = self.create_db_config_stage(name="profile", order = 1)
        self.stage2 = self.create_db_config_stage(name="attendance", order = 3)
        self.stage3 = self.create_db_config_stage(name="tastes", order = 2)

    def test_initial_status(self):
        response = self.client.get('/api/user/%i/config_stages' % self.user.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {"nb_stages": 3, "nb_completed": 0, "completion": 0,
                                         "next_stage": {"id": self.stage1.id, "name": "profile",
                                                        "key": self.stage1.key, "description": '',
                                                        "express_description": '', "validity_days": None,
                                                        "status": "empty", "order" : 1}})

    def test_complete_stages(self):
        # Completing one stage
        response = self.client.post('/api/user/%i/config_stages/complete' % self.user.id,
                                    {'stage_key': self.stage1.key})
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/api/user/%i/config_stages' % self.user.id)
        self.assertEqual(response.data["nb_stages"], 3)
        self.assertEqual(response.data["nb_completed"], 1)
        self.assertEqual(response.data["next_stage"]["id"], self.stage3.id)

        # Completing the same stage
        response = self.client.post('/api/user/%i/config_stages/complete' % self.user.id,
                                    {'stage_key': self.stage1.key})
        self.assertEqual(response.status_code, 200)
        response = self.client.get('/api/user/%i/config_stages' % self.user.id)
        self.assertEqual(response.data["nb_completed"], 1)
        self.assertEqual(response.data["next_stage"]["id"], self.stage3.id)

        # Completing an other stage, but the third one
        response = self.client.post('/api/user/%i/config_stages/complete' % self.user.id,
                                    {'stage_key': self.stage3.key})
        response = self.client.get('/api/user/%i/config_stages' % self.user.id)
        self.assertEqual(response.data["nb_completed"], 2)
        self.assertEqual(response.data["next_stage"]["id"], self.stage2.id)

        # With all stages completed
        response = self.client.post('/api/user/%i/config_stages/complete' % self.user.id,
                                    {'stage_key': self.stage2.key})
        response = self.client.get('/api/user/%i/config_stages' % self.user.id)
        self.assertEqual(response.data["next_stage"], None)
        self.assertEqual(response.data["nb_completed"], 3)

    def test_stage_validity(self):
        # Stage 1 must be updated every 10 days
        self.stage1.validity_days = 10
        self.stage1.save()

        # Completing it now, all right
        response = self.client.post('/api/user/%i/config_stages/complete' % self.user.id,
                                    {'stage_key': self.stage1.key})
        response = self.client.get('/api/user/%i/config_stages' % self.user.id)
        self.assertEqual(response.data["nb_completed"], 1)

        # Wait, no, it was 15 days ago
        completion = ConfigStageCompletion.objects.get(user_id=self.user.id)
        completion.date = timezone.now() - datetime.timedelta(days=15)
        completion.save()

        # Now it needs to be updated
        response = self.client.get('/api/user/%i/config_stages' % self.user.id)
        self.assertEqual(response.data["nb_completed"], 0)
        self.assertEqual(response.data["next_stage"]["id"], self.stage1.id)
        self.assertEqual(response.data["next_stage"]["status"], "expired")

        # Let's update it
        response = self.client.post('/api/user/%i/config_stages/complete' % self.user.id,
                                    {'stage_key': self.stage1.key})
        response = self.client.get('/api/user/%i/config_stages' % self.user.id)
        self.assertEqual(response.data["next_stage"]["id"], self.stage3.id)

    def test_stage_resource(self):
        """
        Test that the stage resource is working correctly with the added-infos
        """
        response = self.client.get('/api/config_stage')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 3)

        response = self.client.get('/api/config_stage', {"user_id": self.user.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 3)
        for elt in response.data:
            self.assertEqual(elt['status'], "empty")

        # Stage 1 must be updated every 10 days
        self.stage1.validity_days = 10
        self.stage1.save()

        # Stage 2 and Stage 1 have been completed 15 days ago
        fifteen_days_ago = timezone.now() - datetime.timedelta(days=15)
        for stage in (self.stage1, self.stage2):
            csc = ConfigStageCompletion.objects.create(user_id=self.user.id, stage_id=stage.id)
            csc.date = fifteen_days_ago
            csc.save()

        response = self.client.get('/api/config_stage', {"user_id": self.user.id})
        self.assertEqual(response.status_code, 200)
        stage_statuses = [elt['status'] for elt in response.data]
        self.assertEqual(stage_statuses, ['expired', 'empty', 'filled'])


class TestBudgetProteins(TestAPIWithLogin):
    
    def setUp(self):
        super().setUp()
        self.create_db_meta_planning()
        
    
    def test_get_set(self):
        # Get defaults
        response = self.client.get('/api/user/%i/budget_proteins' % self.user.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {"budget": 2, "meat": 2, "fish": 2})
        
        # Set 
        NEW_VALUES = {"budget": 3, "meat": 1, "fish": 3}
        response = self.client.post('/api/user/%i/set_budget_proteins' % self.user.id,
                                    NEW_VALUES)
        self.assertEqual(response.status_code, 200)
        
        # Get after modifications
        response = self.client.get('/api/user/%i/budget_proteins' % self.user.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, NEW_VALUES)
        
        
class TestPreconfigure(TestAPIWithLogin):
    
    @patch.object(planning_mgr.controller.meta, 'DefaultPlanningBuilder')
    def test_called_with_correct_arguments(self, mock_planning_builder):
        self.user.budget = 3
        self.user.save()
        
        response = self.client.post('/api/user/%i/preconfigure' % self.user.id,
                                    {'speed': 1})
        self.assertEqual(response.status_code, 200)
        
        mock_planning_builder.assert_called_once()
        args, kwargs = mock_planning_builder.call_args
        
        reload_object(self.user)
        self.assertTrue(args[0].id, self.user.meta_planning_id)
        self.assertTrue(args[1], 1)
        self.assertTrue(args[2], 3)
        
        