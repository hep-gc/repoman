# A test script for repoman-client.
# INCOMPLETE
#
#

import unittest
from repoman_client import repoman_client
import sys

class testRepomanClient(unittest.TestCase):

    """

    A test class for the Repoman client.

    """



    def setUp(self):

        self.repo = repoman_client.repoman_client()


    def testCreateUser(self):
        resp = self.repo.rut.create_user(self.repo.repository, self.repo.usercert, self.repo.userkey, {'user_name': 'test', 'email': 'test@testtest.com', 'cert_dn':'TestDN', 'full_name':'Test Testerson'})
        self.assertEqual(resp.status,200)
        
    def testDescribeUser(self):
        expecteduser = '{"groups": ["'+self.repo.repository+'/api/groups/users"], "full_name": "Test Testerson", "client_dn": "TestDN", "suspended": false, "images": [], "user_name": "test", "email": "test@testtest.com", "permissions": ["image_create", "user_modify_self"]}'
        resp = self.repo.rut.query_user(self.repo.repository, self.repo.usercert, self.repo.userkey, 'test')
        self.assertEqual(resp.read(), expecteduser)
        
        
    def testRemoveUser(self):
        resp = self.repo.rut.remove_user(self.repo.repository, self.repo.usercert, self.repo.userkey, 'test_user').status
        self.assertEqual(resp, 200)
        
    def testCreateGroup(self):
        resp = self.repo.rut.create_group(self.repo.repository, self.repo.usercert, self.repo.userkey, {'name': 'test_group'})
        self.assertEqual(resp.status, 200)
    
    def testDescribeGroup(self):
        # TODO
        expecteduser = '{"groups": ["'+self.repo.repository+'/api/groups/users"], "full_name": "Test Testerson", "client_dn": "TestDN", "suspended": false, "images": [], "user_name": "test", "email": "test@testtest.com", "permissions": ["image_create", "user_modify_self"]}'
        resp = self.repo.rut.query_user(self.repo.repository, self.repo.usercert, self.repo.userkey, 'test_group')
        self.assertEqual(resp.read(), expecteduser)
    
    def testRemoveGroup(self):
        # TODO
        resp = self.repo.rut.remove_group(self.repo.repository, self.repo.usercert, self.repo.userkey, 'test_group').status
        self.assertEqual(resp, 200)
        
    def testCreateImage(self):
        resp = repo.rut.post_image_metadata('/api/images', repo.repository, repo.usercert, repo.userkey, metadata = {'name': 'test_image'})
        self.assertEqual(resp.status, 200)
        
    def testDescribeImage(self):
        # TODO
    
    def testRemoveImage(self):
        # TODO
    


def suite():

    suite = unittest.TestSuite()

    suite.addTest(unittest.makeSuite(testRepomanClient))

    return suite



if __name__ == '__main__':

    #unittest.main()



    suiteFew = unittest.TestSuite()

    suiteFew.addTest(testRepomanClient("testCreateUser"))
    # add other tests here

    unittest.TextTestRunner(verbosity=2).run(suite())
