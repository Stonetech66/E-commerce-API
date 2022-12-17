from rest_framework.test import APITestCase, APIClient, RequestsClient

from Users.models import MyUser

class EcommerceTest(APITestCase):

    def setUp(self):
        self.client=APIClient()
        self.c=RequestsClient()
        
    def test_product_list_view(self):
        response=self.client.get("/")
        assert response.status_code == 200
        
    def test_product_detail_view(self):
        resp=self.c.get("http://4adeeceb-4b88-4466-a49e-2d97bdf8c045/")
        self.assertEqual(resp.status_code, 200)


    def test_unauthorized_user_cant_update_product(self):
        resp=self.client.get("http://cart/")
        self.assertEqual(resp.status_code, 403)


