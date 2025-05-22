
from shopping_mgr.tests         import TestBaseShoppingListTest
from shopping_mgr.controller    import fill_shopping_list
from shopping_mgr.models        import ShoppingItem
from shopping_mgr.serializers   import ShoppingListExtendedSerializer

from common.test                import TestAPIWithLogin

from collections                import defaultdict

import json

class TestShoppingListGeneration(TestBaseShoppingListTest):

    def test_shopping_list(self):
        res = ShoppingListExtendedSerializer(self.shopping_list).data
        self.check_shopping_list(res)

    def test_shopping_list_api(self):
        with self.assertNumQueries(18):
            response = self.client.get('/api/user/%i/shopping_list/%i' % (self.user.id, self.shopping_list.id))
            self.assertEqual(response.status_code, 200)
            self.check_shopping_list(response.data['content'])
            self.assertEqual(response.data['start_date'].strftime("%Y-%m-%d"), "2014-07-08")
            self.assertEqual(response.data['end_date'].strftime("%Y-%m-%d"), "2014-07-11")

class TestCheckUncheck(TestBaseShoppingListTest):

    def test_toggle_item(self):
        def _toggle(shopping_item_id):
            response = self.client.post('/api/user/%i/shopping_list/toggle_item/%i' % (self.user.id,
                                                                                       shopping_item_id))
            self.assertEqual(response.status_code, 200)

        def _num_items_stored():
            return ShoppingItem.objects.filter(shopping_list=self.shopping_list, got_it=True).count()

        # Initially only chocolate is checked (non fresh
        self.assertEqual(_num_items_stored(), 1)

        chocolate_item = ShoppingItem.objects.get(shopping_list=self.shopping_list, food=self.chocolate)
        thing_item = ShoppingItem.objects.get(shopping_list=self.shopping_list, food=self.things)

        _toggle(chocolate_item.id)
        self.assertEqual(_num_items_stored(), 0)
        _toggle(thing_item.id)
        _toggle(chocolate_item.id)
        self.assertEqual(_num_items_stored(),2)

class TestWithLoss(TestBaseShoppingListTest):
    """
    Testing the loss of conversions is correctly taken into account
    """
    FILL_LIST = False

    def _init_default_conversion(self, food):
        """
        The default conversion of carrots is still lossless.
        The default conversion of chocolate is 50%
        """
        res = super()._init_default_conversion(food)
        if food.name == "chocolate":
            res.loss_coeff = 0.5
            res.save()
        return res

    def test_loss_coeff_consequences(self):
        # We test two things :
        # - default conversion without loss and chosen conversion with loss  (small carrots)
        # - default conversion with loss and chosen conversion without loss (chocolate chunks)

        # Small carrots now have 50% loss !
        self.small_carrot_cnv.loss_coeff = 0.5
        self.small_carrot_cnv.save()

        # Removing big_carrot conversion
        self.big_carrot_cnv.delete()

        # So we'll need 18 small carrots instead of 9
        fill_shopping_list(self.shopping_list)
        res = ShoppingListExtendedSerializer(self.shopping_list).data
        self.assertEqual(res[0]['items'][0]['conversion']['value'], 18)

        # Because chocolate default conversion included a 50% loss,
        # we need 3.5 chunk of chocolate instead of 7
        self.assertEqual(res[0]['items'][2]['conversion']['value'], 3.5)
