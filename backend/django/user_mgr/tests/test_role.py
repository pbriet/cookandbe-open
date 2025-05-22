
from common.test                import OptalimTest
from user_mgr.models            import Role

import json

TEST_ROLES = {
    "admin": Role.R_ADMIN,
    "useless": 42,
}

class TestRole(OptalimTest):
    INIT_CLIENT_API = True
    PERMISSIONS = ("admin", )

    def init_default_roles(self):
        self.roles = dict()
        for role_name, role_id in TEST_ROLES.items():
            self.roles[role_name] = self.create_db_role(role_name, id=role_id)

    def check_get_list(self, expected_status):
        response = self.client.get('/api/role')
        self.assertEqual(response.status_code, expected_status)

    def check_set_role(self, expected_status):
        response = self.client.post('/api/role')
        self.assertEqual(response.status_code, expected_status)

    def check_get_role(self, expected_status):
        response = self.client.get('/api/role/%i' % self.roles["admin"].id)
        self.assertEqual(response.status_code, expected_status)

    def check_add_user_role(self, expected_status):
        response = self.client.post('/secure/api/user/%i/add_role' % self.user.id,
                                    json.dumps({ "role_id" : self.roles["useless"].id }),
                                    content_type = "application/json")
        self.assertEqual(response.status_code, expected_status)

    def check_del_user_role(self, expected_status):
        response = self.client.post('/secure/api/user/%i/remove_role' % self.user.id,
                                    json.dumps({ "role_id" : self.roles["useless"].id }),
                                    content_type = "application/json")
        self.assertEqual(response.status_code, expected_status)

    def test_anonymous_roles_api(self):
        self.assertFalse(self.is_authenticated())

        self.check_get_list(401)
        self.check_set_role(401)
        self.check_get_role(401)
        self.check_add_user_role(401)
        self.check_del_user_role(401)

    def test_user_roles_api(self):
        # Remove all privileges
        self.user.user_roles.all().delete()
        # Login
        self.change_user(self.user)
        self.assertFalse(self.user.is_admin)

        self.check_get_list(403)
        self.check_set_role(403)
        self.check_get_role(403)
        self.check_add_user_role(403)
        self.check_del_user_role(403)

    def test_admin_roles_api(self):
        # Login
        self.change_user(self.user)
        self.assertTrue(self.user.is_admin)

        self.check_get_list(200)
        self.check_set_role(403)
        self.check_get_role(200)
        self.check_add_user_role(200)
        self.check_add_user_role(400) # Double add
        self.check_del_user_role(200)
        self.check_del_user_role(400) # Double del
