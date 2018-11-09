# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.addons.shopinvader.tests.common import ProductCommonCase
from odoo.addons.storage_image_product.tests.common import (
    ProductImageCommonCase)


class TestShopinvaderBackendTest(ProductCommonCase, ProductImageCommonCase):
    """
    Tests for shopinvader.backend
    """

    def setUp(self):
        super(TestShopinvaderBackendTest, self).setUp()
        self.backend.write({
            'image_proxy_url': 'custom.website.dev',
        })
        self.env.ref('base.user_demo').write({
            'groups_id': [
                (4, self.env.ref('shopinvader.group_shopinvader_manager').id)]
        })
        ProductImageCommonCase.setUp(self)
        img_relation_obj = self.env['product.image.relation']
        product_attr = self.env.ref('product.product_attribute_value_4')
        self.logo = img_relation_obj.create({
            'product_tmpl_id': self.template.id,
            'image_id': self.logo_image.id,
        })
        self.image_bk = img_relation_obj.create({
            'product_tmpl_id': self.template.id,
            'image_id': self.black_image.id,
            'attribute_value_ids': [(6, 0, product_attr.ids)]
        })

    def test_replace_url(self):
        """
        Test if the url is correctly replaced
        :return:
        """
        # Test normal url
        image_proxy_url = self.backend.image_proxy_url
        # Normal url with final /
        test_url = "https://aaaaaaaa.bbbbbbbb.dev/"
        expected_url = "https://%s/" % image_proxy_url
        result_url = self.backend._replace_by_proxy(test_url)
        self.assertEqual(expected_url, result_url)
        # Normal url without final /
        test_url = "https://aaaaaaaa.bbbbbbbb.dev"
        expected_url = "https://%s" % image_proxy_url
        result_url = self.backend._replace_by_proxy(test_url)
        self.assertEqual(expected_url, result_url)
        # Test url with arguments
        test_url = "https://aaaaaaaa.xxxx.dev/get?a=5698zzzz"
        expected_url = "https://%s/get?a=5698zzzz" % image_proxy_url
        result_url = self.backend._replace_by_proxy(test_url)
        self.assertEqual(expected_url, result_url)
        # Test url without subdomain
        test_url = "https://xxxx.dev/get?a=5698zzzzea"
        expected_url = "https://%s/get?a=5698zzzzea" % image_proxy_url
        result_url = self.backend._replace_by_proxy(test_url)
        self.assertEqual(expected_url, result_url)
        # Test url with another protocol
        test_url = "ftp://xxxx.dev/get?a=5698zzzzqqq"
        expected_url = "ftp://%s/get?a=5698zzzzqqq" % image_proxy_url
        result_url = self.backend._replace_by_proxy(test_url)
        self.assertEqual(expected_url, result_url)
        # Now remove the image_proxy_url on the backend
        # So the given url shouldn't be updated
        self.backend.write({
            'image_proxy_url': False,
        })
        test_url = "https://aaaaaaaa.bbbbbbbb.dev/"
        result_url = self.backend._replace_by_proxy(test_url)
        self.assertEqual(test_url, result_url)
        test_url = "https://xxxx.dev/get?a=5698zzzzea"
        result_url = self.backend._replace_by_proxy(test_url)
        self.assertEqual(test_url, result_url)
        test_url = "https://aaaa.xxxx.dev/get?a=5698zzzzea"
        result_url = self.backend._replace_by_proxy(test_url)
        self.assertEqual(test_url, result_url)
