import os
import sys
# Need to access identity module
sys.path.append(os.path.abspath(os.path.join(os.path.abspath(__file__),
                                '..', '..', '..', '..', 'keystone')))
import unittest
import httplib2
import json
from lxml import etree
import test_common as utils


class TenantTest(unittest.TestCase):

    def setUp(self):
        self.tenant = 'test_tenant'
        self.token = utils.get_token('joeuser', 'secrete', self.tenant,
                                     'token')
        self.user = utils.get_user()
        self.userdisabled = utils.get_userdisabled()
        self.auth_token = utils.get_auth_token()
        self.exp_auth_token = utils.get_exp_auth_token()
        self.disabled_token = utils.get_disabled_token()

    def tearDown(self):
        resp, content = utils.delete_tenant(self.tenant, self.auth_token)


class CreateTenantTest(TenantTest):

    def test_tenant_create(self):
        resp, content = utils.delete_tenant(self.tenant, str(self.auth_token))
        resp, content = utils.create_tenant(self.tenant, str(self.auth_token))
        if int(resp['status']) == 500:
            self.fail('IDM fault')
        elif int(resp['status']) == 503:
            self.fail('Service Not Available')

        if int(resp['status']) not in (200, 201):

            self.fail('Failed due to %d' % int(resp['status']))

    def test_tenant_create_xml(self):
        resp, content = utils.delete_tenant_xml(self.tenant,
                                                str(self.auth_token))
        resp, content = utils.create_tenant_xml(self.tenant,
                                                str(self.auth_token))
        content = etree.fromstring(content)
        if int(resp['status']) == 500:
            self.fail('IDM fault')
        elif int(resp['status']) == 503:
            self.fail('Service Not Available')
        if int(resp['status']) not in (200, 201):
            self.fail('Failed due to %d' % int(resp['status']))

    def test_tenant_create_again(self):

        resp, content = utils.create_tenant(self.tenant,
                                            str(self.auth_token))
        if int(resp['status']) == 200:
            self.tenant = content['tenant']['id']
        resp, content = utils.create_tenant(self.tenant,
                                            str(self.auth_token))
        if int(resp['status']) == 500:
            self.fail('IDM fault')
        elif int(resp['status']) == 503:
            self.fail('Service Not Available')
        self.assertEqual(409, int(resp['status']))

    def test_tenant_create_again_xml(self):

        resp, content = utils.create_tenant_xml(self.tenant,
                                                str(self.auth_token))
        resp, content = utils.create_tenant_xml(self.tenant,
                                                str(self.auth_token))
        content = etree.fromstring(content)
        if int(resp['status']) == 500:
            self.fail('IDM fault')
        elif int(resp['status']) == 503:
            self.fail('Service Not Available')
        self.assertEqual(409, int(resp['status']))

    def test_tenant_create_forbidden_token(self):
        header = httplib2.Http(".cache")
        resp, content = utils.create_tenant(self.tenant, str(self.auth_token))
        if int(resp['status']) == 200:
            self.tenant = content['tenant']['id']

        url = '%stenants' % (utils.URL)
        body = {"tenant": {"id": self.tenant,
                           "description": "A description ...",
                           "enabled": True}}
        resp, content = header.request(url, "POST", body=json.dumps(body),
                                  headers={"Content-Type": "application/json",
                                         "X-Auth-Token": self.token})

        if int(resp['status']) == 500:
            self.fail('IDM fault')
        elif int(resp['status']) == 503:
            self.fail('Service Not Available')
        self.assertEqual(401, int(resp['status']))

    def test_tenant_create_forbidden_token_xml(self):
        header = httplib2.Http(".cache")
        resp, content = utils.create_tenant_xml(self.tenant,
                                                str(self.auth_token))
        content = etree.fromstring(content)
        if int(resp['status']) == 200:
            self.tenant = content.get('id')

        url = '%stenants' % (utils.URL)
        body = '<?xml version="1.0" encoding="UTF-8"?> \
            <tenant xmlns="http://docs.openstack.org/idm/api/v1.0" \
            enabled="true" id="%s"> \
            <description>A description...</description> \
            </tenant>' % self.tenant
        resp, content = header.request(url, "POST", body=body,
                                  headers={"Content-Type": "application/xml",
                                           "X-Auth-Token": self.token,
                                           "ACCEPT": "application/xml"})

        if int(resp['status']) == 500:
            self.fail('IDM fault')
        elif int(resp['status']) == 503:
            self.fail('Service Not Available')
        self.assertEqual(401, int(resp['status']))

    def test_tenant_create_expired_token(self):
        header = httplib2.Http(".cache")
        resp, content = utils.create_tenant(self.tenant,
                                            str(self.auth_token))
        if int(resp['status']) == 200:
            self.tenant = content['tenant']['id']
        url = '%stenants' % (utils.URL)
        body = {"tenant": {"id": self.tenant,
                           "description": "A description ...",
                           "enabled": True}}
        resp, content = header.request(url, "POST", body=json.dumps(body),
                                headers={"Content-Type": "application/json",
                                         "X-Auth-Token": self.exp_auth_token})
        if int(resp['status']) == 500:
            self.fail('IDM fault')
        elif int(resp['status']) == 503:
            self.fail('Service Not Available')
        self.assertEqual(403, int(resp['status']))

    def test_tenant_create_expired_token_xml(self):
        header = httplib2.Http(".cache")
        resp, content = utils.create_tenant_xml(self.tenant,
                                                str(self.auth_token))
        content = etree.fromstring(content)
        if int(resp['status']) == 200:
            self.tenant = content.get('id')

        url = '%stenants' % (utils.URL)
        body = '<?xml version="1.0" encoding="UTF-8"?> \
            <tenant xmlns="http://docs.openstack.org/idm/api/v1.0" \
            enabled="true" id="%s"> \
            <description>A description...</description> \
            </tenant>' % self.tenant

        resp, content = header.request(url, "POST", body=body,
                                  headers={"Content-Type": "application/xml",
                                           "X-Auth-Token": self.exp_auth_token,
                                           "ACCEPT": "application/xml"})

        if int(resp['status']) == 500:
            self.fail('IDM fault')
        elif int(resp['status']) == 503:
            self.fail('Service Not Available')
        self.assertEqual(403, int(resp['status']))

    def test_tenant_create_missing_token(self):
        header = httplib2.Http(".cache")
        resp, content = utils.create_tenant(self.tenant,
                                            str(self.auth_token))
        if int(resp['status']) == 200:
            self.tenant = content['tenant']['id']

        url = '%stenants' % (utils.URL)
        body = {"tenant": {"id": self.tenant,
                           "description": "A description ...",
                           "enabled": True}}
        resp, content = header.request(url, "POST", body=json.dumps(body),
                                headers={"Content-Type": "application/json"})

        if int(resp['status']) == 500:
            self.fail('IDM fault')
        elif int(resp['status']) == 503:
            self.fail('Service Not Available')
        self.assertEqual(401, int(resp['status']))

    def test_tenant_create_missing_token_xml(self):
        header = httplib2.Http(".cache")
        resp, content = utils.create_tenant_xml(self.tenant,
                                                str(self.auth_token))
        content = etree.fromstring(content)
        if int(resp['status']) == 200:
            self.tenant = content.get('id')
        url = '%stenants' % (utils.URL)
        body = '<?xml version="1.0" encoding="UTF-8"?> \
            <tenant xmlns="http://docs.openstack.org/idm/api/v1.0" \
            enabled="true" id="%s"> \
            <description>A description...</description> \
            </tenant>' % self.tenant
        resp, content = header.request(url, "POST", body=body,
                                  headers={"Content-Type": "application/xml",
                                           "ACCEPT": "application/xml"})
        if int(resp['status']) == 500:
            self.fail('IDM fault')
        elif int(resp['status']) == 503:
            self.fail('Service Not Available')
        self.assertEqual(401, int(resp['status']))

    def test_tenant_create_disabled_token(self):
        header = httplib2.Http(".cache")
        resp, content = utils.create_tenant(self.tenant,
                                            str(self.auth_token))
        if int(resp['status']) == 200:
            self.tenant = content['tenant']['id']

        url = '%stenants' % (utils.URL)
        body = '{"tenant": { "id": "%s", \
                "description": "A description ...", "enabled"\
                :true  } }' % self.tenant
        resp, content = header.request(url, "POST", body=body,
                                  headers={"Content-Type": "application/json",
                                        "X-Auth-Token": self.disabled_token})

        if int(resp['status']) == 500:
            self.fail('IDM fault')
        elif int(resp['status']) == 503:
            self.fail('Service Not Available')
        self.assertEqual(403, int(resp['status']))

    def test_tenant_create_disabled_token_xml(self):
        header = httplib2.Http(".cache")
        resp, content = utils.create_tenant_xml(self.tenant,
                                                str(self.auth_token))
        content = etree.fromstring(content)
        if int(resp['status']) == 200:
            self.tenant = content.get('id')
        url = '%stenants' % (utils.URL)
        body = '<?xml version="1.0" encoding="UTF-8"?> \
            <tenant xmlns="http://docs.openstack.org/idm/api/v1.0" \
            enabled="true" id="%s"> \
            <description>A description...</description> \
            </tenant>' % self.tenant
        resp, content = header.request(url, "POST", body=body,
                                  headers={"Content-Type": "application/xml",
                                           "X-Auth-Token": self.disabled_token,
                                           "ACCEPT": "application/xml"})
        if int(resp['status']) == 500:
            self.fail('IDM fault')
        elif int(resp['status']) == 503:
            self.fail('Service Not Available')
        self.assertEqual(403, int(resp['status']))

    def test_tenant_create_invalid_token(self):
        header = httplib2.Http(".cache")
        resp, content = utils.create_tenant(self.tenant,
                                            str(self.auth_token))
        if int(resp['status']) == 200:
            self.tenant = content['tenant']['id']

        url = '%stenants' % (utils.URL)
        body = '{"tenant": { "id": "%s", \
                "description": "A description ...", "enabled"\
                :true  } }' % self.tenant
        resp, content = header.request(url, "POST", body=body,
                                  headers={"Content-Type": "application/json",
                                           "X-Auth-Token": 'nonexsitingtoken'})

        if int(resp['status']) == 500:
            self.fail('IDM fault')
        elif int(resp['status']) == 503:
            self.fail('Service Not Available')
        self.assertEqual(404, int(resp['status']))

    def test_tenant_create_invalid_token_xml(self):
        header = httplib2.Http(".cache")
        resp, content = utils.create_tenant_xml(self.tenant,
                                                str(self.auth_token))
        content = etree.fromstring(content)
        if int(resp['status']) == 200:
            self.tenant = content.get('id')

        url = '%stenants' % (utils.URL)
        body = '<?xml version="1.0" encoding="UTF-8"?> \
            <tenant xmlns="http://docs.openstack.org/idm/api/v1.0" \
            enabled="true" id="%s"> \
            <description>A description...</description> \
            </tenant>' % self.tenant
        resp, content = header.request(url, "POST", body=body,
                                  headers={"Content-Type": "application/xml",
                                           "X-Auth-Token": 'nonexsitingtoken',
                                           "ACCEPT": "application/xml"})

        if int(resp['status']) == 500:
            self.fail('IDM fault')
        elif int(resp['status']) == 503:
            self.fail('Service Not Available')
        self.assertEqual(404, int(resp['status']))


class GetTenantsTest(TenantTest):

    def test_get_tenants(self):
        header = httplib2.Http(".cache")
        resp, content = utils.create_tenant(self.tenant, str(self.auth_token))
        url = '%stenants' % (utils.URL)
        #test for Content-Type = application/json
        resp, content = header.request(url, "GET", body='{}',
                                  headers={"Content-Type": "application/json",
                                         "X-Auth-Token": self.auth_token})
        if int(resp['status']) == 500:
            self.fail('IDM fault')
        elif int(resp['status']) == 503:
            self.fail('Service Not Available')
        self.assertEqual(200, int(resp['status']))

    def test_get_tenants_xml(self):
        header = httplib2.Http(".cache")
        resp, content = utils.create_tenant(self.tenant, str(self.auth_token))
        url = '%stenants' % (utils.URL)
        #test for Content-Type = application/json
        resp, content = header.request(url, "GET", body='',
                                  headers={"Content-Type": "application/xml",
                                           "X-Auth-Token": self.auth_token,
                                           "ACCEPT": "application/xml"})
        if int(resp['status']) == 500:
            self.fail('IDM fault')
        elif int(resp['status']) == 503:
            self.fail('Service Not Available')
        self.assertEqual(200, int(resp['status']))

    def test_get_tenants_unauthorized_token(self):
        header = httplib2.Http(".cache")
        resp, content = utils.create_tenant(self.tenant, str(self.auth_token))
        url = '%stenants' % (utils.URL)
        #test for Content-Type = application/json
        resp, content = header.request(url, "GET", body='{}',
                                  headers={"Content-Type": "application/json",
                                           "X-Auth-Token": self.token})
        if int(resp['status']) == 500:
            self.fail('IDM fault')
        elif int(resp['status']) == 503:
            self.fail('Service Not Available')
        self.assertEqual(401, int(resp['status']))

    def test_get_tenants_unauthorized_token_xml(self):
        header = httplib2.Http(".cache")
        resp, content = utils.create_tenant(self.tenant, str(self.auth_token))
        url = '%stenants' % (utils.URL)
        #test for Content-Type = application/json
        resp, content = header.request(url, "GET", body='',
                                  headers={"Content-Type": "application/xml",
                                           "X-Auth-Token": self.token,
                                           "ACCEPT": "application/xml"})
        if int(resp['status']) == 500:
            self.fail('IDM fault')
        elif int(resp['status']) == 503:
            self.fail('Service Not Available')
        self.assertEqual(401, int(resp['status']))

    def test_get_tenants_exp_token(self):
        header = httplib2.Http(".cache")
        resp, content = utils.create_tenant(self.tenant, str(self.auth_token))
        url = '%stenants' % (utils.URL)
        #test for Content-Type = application/json
        resp, content = header.request(url, "GET", body='{}',
                                  headers={"Content-Type": "application/json",
                                        "X-Auth-Token": self.exp_auth_token})
        if int(resp['status']) == 500:
            self.fail('IDM fault')
        elif int(resp['status']) == 503:
            self.fail('Service Not Available')
        self.assertEqual(403, int(resp['status']))

    def test_get_tenants_exp_token_xml(self):
        header = httplib2.Http(".cache")
        resp, content = utils.create_tenant(self.tenant, str(self.auth_token))
        url = '%stenants' % (utils.URL)
        #test for Content-Type = application/json
        resp, content = header.request(url, "GET", body='',
                                  headers={"Content-Type": "application/xml",
                                           "X-Auth-Token": self.exp_auth_token,
                                           "ACCEPT": "application/xml"})
        if int(resp['status']) == 500:
            self.fail('IDM fault')
        elif int(resp['status']) == 503:
            self.fail('Service Not Available')
        self.assertEqual(403, int(resp['status']))


class GetTenantTest(TenantTest):

    def test_get_tenant(self):
        header = httplib2.Http(".cache")
        resp, content = utils.create_tenant(self.tenant, str(self.auth_token))
        url = '%stenants/%s' % (utils.URL, self.tenant)
        #test for Content-Type = application/json
        resp, content = header.request(url, "GET", body='{}',
                                  headers={"Content-Type": "application/json",
                                           "X-Auth-Token": self.auth_token})
        if int(resp['status']) == 500:
            self.fail('IDM fault')
        elif int(resp['status']) == 503:
            self.fail('Service Not Available')
        self.assertEqual(200, int(resp['status']))

    def test_get_tenant_xml(self):
        header = httplib2.Http(".cache")
        resp, content = utils.create_tenant(self.tenant, str(self.auth_token))
        url = '%stenants/%s' % (utils.URL, self.tenant)
        #test for Content-Type = application/json
        resp, content = header.request(url, "GET", body='',
                                  headers={"Content-Type": "application/xml",
                                           "X-Auth-Token": self.auth_token,
                                           "ACCEPT": "application/xml"})
        if int(resp['status']) == 500:
            self.fail('IDM fault')
        elif int(resp['status']) == 503:
            self.fail('Service Not Available')
        self.assertEqual(200, int(resp['status']))

    def test_get_tenant_bad(self):
        header = httplib2.Http(".cache")
        resp, content = utils.create_tenant(self.tenant, str(self.auth_token))
        url = '%stenants/%s' % (utils.URL, 'tenant_bad')
        #test for Content-Type = application/json
        resp, content = header.request(url, "GET", body='',
                                  headers={"Content-Type": "application/json",
                                           "X-Auth-Token": self.auth_token})
        if int(resp['status']) == 500:
            self.fail('IDM fault')
        elif int(resp['status']) == 503:
            self.fail('Service Not Available')
        self.assertEqual(404, int(resp['status']))

    def test_get_tenant_bad_xml(self):
        header = httplib2.Http(".cache")
        resp, content = utils.create_tenant(self.tenant, str(self.auth_token))
        url = '%stenants/%s' % (utils.URL, 'tenant_bad')
        #test for Content-Type = application/json
        resp, content = header.request(url, "GET", body='',
                                  headers={"Content-Type": "application/xml",
                                           "X-Auth-Token": self.auth_token,
                                           "ACCEPT": "application/xml"})
        if int(resp['status']) == 500:
            self.fail('IDM fault')
        elif int(resp['status']) == 503:
            self.fail('Service Not Available')
        self.assertEqual(404, int(resp['status']))

    def test_get_tenant_not_found(self):
        header = httplib2.Http(".cache")
        resp, content = utils.create_tenant(self.tenant, str(self.auth_token))
        url = '%stenants/NonexistingID' % (utils.URL)
        #test for Content-Type = application/json
        resp, content = header.request(url, "GET", body='{}',
                                  headers={"Content-Type": "application/json",
                                           "X-Auth-Token": self.auth_token})
        if int(resp['status']) == 500:
            self.fail('IDM fault')
        elif int(resp['status']) == 503:
            self.fail('Service Not Available')
        self.assertEqual(404, int(resp['status']))

    def test_get_tenant_not_found_xml(self):
        header = httplib2.Http(".cache")
        resp, content = utils.create_tenant(self.tenant, str(self.auth_token))
        url = '%stenants/NonexistingID' % (utils.URL)
        #test for Content-Type = application/json
        resp, content = header.request(url, "GET", body='',
                                  headers={"Content-Type": "application/xml",
                                           "X-Auth-Token": self.auth_token,
                                           "ACCEPT": "application/xml"})
        if int(resp['status']) == 500:
            self.fail('IDM fault')
        elif int(resp['status']) == 503:
            self.fail('Service Not Available')
        self.assertEqual(404, int(resp['status']))


class UpdateTenantTest(TenantTest):

    def test_update_tenant(self):
        header = httplib2.Http(".cache")
        resp, content = utils.create_tenant(self.tenant, str(self.auth_token))
        url = '%stenants/%s' % (utils.URL, self.tenant)
        data = '{"tenant": { "description": "A NEW description..." ,\
                "enabled":true }}'
        #test for Content-Type = application/json
        resp, content = header.request(url, "PUT", body=data,
                                  headers={"Content-Type": "application/json",
                                           "X-Auth-Token": self.auth_token})
        body = json.loads(content)
        if int(resp['status']) == 500:
            self.fail('IDM fault')
        elif int(resp['status']) == 503:
            self.fail('Service Not Available')
        self.assertEqual(200, int(resp['status']))
        self.assertEqual(self.tenant, body['tenant']['id'])
        self.assertEqual('A NEW description...', body['tenant']['description'])

    def test_update_tenant_xml(self):
        header = httplib2.Http(".cache")
        resp, content = utils.create_tenant_xml(self.tenant,
                                                str(self.auth_token))
        url = '%stenants/%s' % (utils.URL, self.tenant)
        data = '<?xml version="1.0" encoding="UTF-8"?> \
             <tenant xmlns="http://docs.openstack.org/idm/api/v1.0" \
             enabled="true"> \
             <description>A NEW description...</description> \
             </tenant>'

        #test for Content-Type = application/json
        resp, content = header.request(url, "PUT", body=data,
                                  headers={"Content-Type": "application/xml",
                                           "X-Auth-Token": self.auth_token,
                                           "ACCEPT": "application/xml"})
        body = etree.fromstring(content)
        desc = body.find("{http://docs.openstack.org/idm/api/v1.0}description")
        if int(resp['status']) == 500:
            self.fail('IDM fault')
        elif int(resp['status']) == 503:
            self.fail('Service Not Available')
        self.assertEqual(200, int(resp['status']))
        self.assertEqual(self.tenant, body.get('id'))
        self.assertEqual('A NEW description...', desc.text)

    def test_update_tenant_bad(self):
        header = httplib2.Http(".cache")
        resp, content = utils.create_tenant(self.tenant, str(self.auth_token))
        url = '%stenants/%s' % (utils.URL, self.tenant)
        data = '{"tenant": { "description_bad": "A NEW description...",\
                "enabled":true  }}'
        #test for Content-Type = application/json

        resp, content = header.request(url, "PUT", body=data,
                                  headers={"Content-Type": "application/json",
                                           "X-Auth-Token": self.auth_token})
        if int(resp['status']) == 500:
            self.fail('IDM fault')
        elif int(resp['status']) == 503:
            self.fail('Service Not Available')
        self.assertEqual(400, int(resp['status']))

    def test_update_tenant_bad_xml(self):
        header = httplib2.Http(".cache")
        resp, content = utils.create_tenant(self.tenant, str(self.auth_token))
        url = '%stenants/%s' % (utils.URL, self.tenant)
        data = '<?xml version="1.0" encoding="UTF-8"?> \
             <tenant xmlns="http://docs.openstack.org/idm/api/v1.0" \
             enabled="true"> \
             <description_bad>A NEW description...</description> \
             </tenant>'
        #test for Content-Type = application/json
        resp, content = header.request(url, "PUT", body=data,
                                  headers={"Content-Type": "application/xml",
                                           "X-Auth-Token": self.auth_token,
                                           "ACCEPT": "application/xml"})
        if int(resp['status']) == 500:
            self.fail('IDM fault')
        elif int(resp['status']) == 503:
            self.fail('Service Not Available')
        self.assertEqual(400, int(resp['status']))

    def test_update_tenant_not_found(self):
        header = httplib2.Http(".cache")
        resp, content = utils.create_tenant(self.tenant, str(self.auth_token))
        url = '%stenants/NonexistingID' % (utils.URL)
        data = '{"tenant": { "description": "A NEW description...",\
                "enabled":true  }}'
        #test for Content-Type = application/json
        resp, content = header.request(url, "GET", body=data,
                                  headers={"Content-Type": "application/json",
                                           "X-Auth-Token": self.auth_token})
        if int(resp['status']) == 500:
            self.fail('IDM fault')
        elif int(resp['status']) == 503:
            self.fail('Service Not Available')
        self.assertEqual(404, int(resp['status']))

    def test_update_tenant_not_found_xml(self):
        header = httplib2.Http(".cache")
        resp, content = utils.create_tenant(self.tenant, str(self.auth_token))
        url = '%stenants/NonexistingID' % (utils.URL)
        data = '<?xml version="1.0" encoding="UTF-8"?> \
             <tenant xmlns="http://docs.openstack.org/idm/api/v1.0" \
             enabled="true"> \
             <description_bad>A NEW description...</description> \
             </tenant>'
        #test for Content-Type = application/json
        resp, content = header.request(url, "GET", body=data,
                                  headers={"Content-Type": "application/xml",
                                           "X-Auth-Token": self.auth_token,
                                           "ACCEPT": "application/xml"})
        if int(resp['status']) == 500:
            self.fail('IDM fault')
        elif int(resp['status']) == 503:
            self.fail('Service Not Available')
        self.assertEqual(404, int(resp['status']))


class DeleteTenantTest(TenantTest):

    def test_delete_tenant_not_found(self):
        #resp,content=utils.create_tenant("test_tenant_delete",
        #                                str(self.auth_token))
        resp, content = utils.delete_tenant("test_tenant_delete111",
                                      str(self.auth_token))
        self.assertEqual(404, int(resp['status']))

    def test_delete_tenant_not_found_xml(self):
        #resp,content=utils.create_tenant("test_tenant_delete",
        #                                    str(self.auth_token))
        resp, content = utils.delete_tenant_xml("test_tenant_delete111",
                                          str(self.auth_token))
        self.assertEqual(404, int(resp['status']))

    def test_delete_tenant(self):
        resp, content = utils.create_tenant("test_tenant_delete",
                                      str(self.auth_token))
        resp, content = utils.delete_tenant("test_tenant_delete",
                                      str(self.auth_token))
        self.assertEqual(204, int(resp['status']))

    def test_delete_tenant_xml(self):
        resp, content = utils.create_tenant_xml("test_tenant_delete",
                                          str(self.auth_token))
        resp, content = utils.delete_tenant_xml("test_tenant_delete",
                                          str(self.auth_token))
        self.assertEqual(204, int(resp['status']))

if __name__ == '__main__':
    unittest.main()
