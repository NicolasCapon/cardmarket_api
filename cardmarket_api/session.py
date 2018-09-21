import gzip
import base64
from lxml import etree
from cardmarket_api.call import api_request
from cardmarket_api.utils import dict_to_xml


class CardMarketSession:
    """Create a session for specified account"""

    # 5000 requests per 24 hours max
    request_count = 0
    expires = None

    def __init__(self, mkm_app_token, mkm_app_secret, mkm_access_token, mkm_token_secret):
        self.credentials = {"mkm_app_token": mkm_app_token,
                            "mkm_app_secret": mkm_app_secret,
                            "mkm_access_token": mkm_access_token,
                            "mkm_token_secret": mkm_token_secret}

    @api_request
    def get_metaproduct_info(self, metaproduct_id):
        """Return info for metaproduct specified by id"""
        endpoint = "/metaproduct/{0}".format(metaproduct_id)
        data_type = "metaproduct"
        return {"endpoint": endpoint, "data_type": data_type}

    @api_request
    def get_product_info(self, product_id):
        """Return info for product specified by id"""
        endpoint = "/products/{0}".format(product_id)
        data_type = "product"
        return {"endpoint": endpoint, "data_type": data_type}

    @api_request
    def get_products_by_name(self, card_name, exact=False, id_language=1):
        """Return a list of product from card_name either in English or French.
           card_name has to be an exact match
           English idLanguage = 1
           French idLanguage = 2"""
        endpoint = "/products/find"
        parameters = {"search": card_name, "exact": exact, "idGame": 1, "idLanguage": id_language}
        return {"endpoint": endpoint, "data_type": "product", "parameters": parameters}

    @api_request
    def get_articles_for_sale(self, product_id):
        """Return list of all articles for sale for a specified article"""
        endpoint = "/articles/{0}".format(product_id)
        data_type = "article"
        return {"endpoint": endpoint, "data_type": data_type}

    def get_all_products(self):
        """Return binary list of all cardMarket products. Use 'wb' to write down"""
        gzip_file = self.get_all_products_file()
        data = gzip.decompress(base64.b64decode(gzip_file))
        return data

    @api_request
    def get_all_products_file(self):
        """Return gzip file with all cardMarket products"""
        endpoint = "/productlist"
        data_type = "productsfile"
        return {"endpoint": endpoint, "data_type": data_type}

    @api_request
    def get_all_expansions(self):
        """Return list of all expansions"""
        endpoint = "/games/1/expansions"
        return {"endpoint": endpoint}

    @api_request
    def get_wantlists(self):
        """Return list of all wantLists of the account"""
        endpoint = "/wantslist"
        data_type = "wantslist"
        return {"endpoint": endpoint, "data_type": data_type}

    @api_request
    def get_cards_from_wantlist(self, id):
        """Return list of cards from specified wantList by id"""
        endpoint = "/wantslist/{0}".format(id)
        data_type = "want"
        return {"endpoint": endpoint, "data_type": data_type}

    @api_request
    def get_shopping_cart(self):
        """Return dict with shippingAddress, shoppingCart and account"""
        endpoint = "/shoppingcart"
        return {"endpoint": endpoint}

    @staticmethod
    def construct_xml(dict_list):
        """Return MKM API valid binary string XML from a list of dict
           For empty SubElement set value to None type"""
        xml_tree = etree.Element("request")
        [dict_to_xml(xml_tree, d) for d in dict_list]
        return etree.tostring(xml_tree, encoding='UTF-8', xml_declaration=True)


if __name__ == "__main__":
    # Tests:
    import crednetials
    cm = CardMarketSession('o8k5KkPRsPcATLlQ',
                           'JzDyGQ4saapNNOWcP52nuqkyByl1Hhtf',
                           'y3KatFEbJymlwf8stIZUJSZrH9PFo4WG',
                           'y83NntEs2t0eYtwRKSnvXgfjmQdTJ6i4')

    print(cm.get_products_by_name("giant spider"))
    print(cm.request_count)
