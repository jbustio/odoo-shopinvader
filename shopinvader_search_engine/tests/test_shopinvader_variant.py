# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from uuid import uuid4
from odoo.addons.shopinvader.tests.common import ProductCommonCase
from odoo.addons.connector_search_engine.tests.common import \
    TestSeBackendCase, TestSeBackend


class TestShopinvaderVariantTest(ProductCommonCase, TestSeBackendCase):
    """
    Tests for shopinvader.variant
    """

    def setUp(self):
        super(TestShopinvaderVariantTest, self).setUp()
        variant_model = self.env['ir.model'].search([
            ('model', '=', self.shopinvader_variants._name),
        ])
        res_lang = self.env['res.lang'].search([], limit=1)
        se_backend = self.env['se.backend'].create({
            'name': 'SE Backend Test',
            'specific_model': TestSeBackend._name,
        })
        self.env[TestSeBackend._name].create({
            'name': 'SE Backend specific Test',
            'se_backend_id': se_backend.id,
        })
        self.exporter = self.env['ir.exports'].create({
            'name': 'Random name for export',
            'resource': self.shopinvader_variants._name,
            'export_fields': [
                (0, False, {
                    'name': 'object_id',
                    'alias': 'object_id:objectID',
                }),
            ]
        })
        index = self.env['se.index'].create({
            'name': 'partner index',
            'backend_id': se_backend.id,
            'model_id': variant_model.id,
            'lang_id': res_lang.id,
            'exporter_id': self.exporter.id,
        })
        self.backend.write({
            'se_backend_id': se_backend.id,
        })
        self.shopinvader_variants.write({
            'index_id': index.id,
        })
        self.shopinvader_variants.mapped("index_id").write({
            'backend_id': se_backend.id,
        })
        self.backend.force_recompute_all_binding_index()

    def _check_expected_seo_name(self, backend, variants):
        """
        Check expected result of _build_seo_product_name
        :param backend: shopinvader.backend
        :param variants: shopinvader.variant
        :return:
        """
        for variant in variants:
            result = variant._build_seo_product_name()
            expected_result = u"{} | {}".format(
                variant.name, backend.website_public_name or u"")
            self.assertEquals(result, expected_result)

    def _check_seo_name(self, variants, equals=True):
        """
        Check if the seo_name of given variants are correct.
        Equals (True) means that the seo_title must match and when it's
        False, they should be equals.
        It useful when the seo_title of the variant has been updated manually
        and shouldn't be updated by the result of _build_seo_product_name().
        :param variants: shopinvader.variant
        :param equals: bool
        :return:
        """
        variants.recompute_json()
        for variant in variants:
            result = variant._build_seo_product_name()
            if equals:
                self.assertEquals(variant.seo_title, result)
            else:
                self.assertNotEqual(variant.seo_title, result)

    def test_public_name_empty(self):
        """
        Test when the website_public_name on the backend is empty
        :return:
        """
        public_name = False
        self.backend.write({
            "website_public_name": public_name,
        })
        self._check_expected_seo_name(self.backend, self.shopinvader_variants)

    def test_public_name_normal(self):
        """
        Test when the website_public_name on the backend is filled
        :return:
        """
        self.backend.write({
            "website_public_name": "Shopinvader redavnipohs",
        })
        self._check_expected_seo_name(self.backend, self.shopinvader_variants)

    def test_public_name_special_char1(self):
        """
        Test when the website_public_name on the backend is filled with some
        special characters
        :return:
        """
        self.backend.write({
            "website_public_name": "Shopinvader éèiï&|ç{ù$µ",
        })
        self._check_expected_seo_name(self.backend, self.shopinvader_variants)

    def test_public_name_special_char2(self):
        """
        Test when the website_public_name on the backend is filled with some
        special characters and also variants
        :return:
        """
        self.backend.write({
            "website_public_name": "Shopinvader éèiï&|ç{ù$µ",
        })
        for variant in self.shopinvader_variants:
            variant.write({
                'name': variant.name + u" éèiï&|ç{ù$µ"
            })
        self._check_expected_seo_name(self.backend, self.shopinvader_variants)

    def test_recompute_json_normal(self):
        """
        Check if the recompute_json update correctly the seo_name of the
        shopinvader.variant (normal behaviour)
        :return:
        """
        self.backend.write({
            "website_public_name": "Shopinvader redavnipohs",
        })
        # For this case, seo_title is empty so it should be updated
        self.shopinvader_variants.write({
            'seo_title': False,
        })
        self._check_seo_name(self.shopinvader_variants)

    def test_recompute_json_special_char(self):
        """
        Check if the recompute_json update correctly the seo_name of the
        shopinvader.variant (normal behaviour but the public name has some
        special characters)
        :return:
        """
        self.backend.write({
            "website_public_name": "Shopinvader éèiï&|ç{ù$µ",
        })
        # For this case, seo_title is empty so it should be updated
        self.shopinvader_variants.write({
            'seo_title': False,
        })
        self._check_seo_name(self.shopinvader_variants)

    def test_recompute_json_already_defined(self):
        """
        Check if the recompute_json update correctly the seo_name of the
        shopinvader.variant (the seo_title is already filled and shouldn't be
        updated)
        :return:
        """
        self.backend.write({
            "website_public_name": "Shopinvader éèiï&|ç{ù$µ",
        })
        # For this case, seo_title is empty so it should be updated
        for variant in self.shopinvader_variants:
            variant.write({
                'seo_title': str(uuid4()),
            })
        self._check_seo_name(self.shopinvader_variants, equals=False)

    def test_recompute_json_empty(self):
        """
        Check if the recompute_json update correctly the seo_name of the
        shopinvader.variant (the public name is not filled so the seo_title
        should stay empty too)
        :return:
        """
        self.backend.write({
            "website_public_name": False,
        })
        # For this case, seo_title is empty so it should be updated
        self.shopinvader_variants.write({
            'seo_title': False,
        })
        self.shopinvader_variants.recompute_json()
        for variant in self.shopinvader_variants:
            self.assertFalse(variant.seo_title)
