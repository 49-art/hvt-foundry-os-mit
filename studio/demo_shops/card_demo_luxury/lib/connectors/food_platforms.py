"""Food delivery marketplaces — listed so salespeople know the options. No public self-serve API for a small shop."""
from . import ConnectorError
from .delivery import _CatalogueOnly


class Deliveroo(_CatalogueOnly):
    id = "deliveroo"
    name = "Deliveroo (restaurant/shop partner)"
    category = "Food delivery"
    cost_type = "paid"
    what_it_does = "Marketplace app: customers order from the shop, Deliveroo riders deliver. Sign-up is a partner application, not an API key."
    docs_url = "https://restaurants.deliveroo.com/"
    status_note = "Catalogue only. Commission and terms not checked today. Use the live search 'delivery' category to see current sign-up pages."


class UberEats(_CatalogueOnly):
    id = "uber_eats"
    name = "Uber Eats (merchant)"
    category = "Food delivery"
    cost_type = "paid"
    what_it_does = "Marketplace app, like Deliveroo. Partner sign-up; API only for approved integrators."
    docs_url = "https://merchants.ubereats.com/gb/en/"
    status_note = "Catalogue only. Terms not checked today."


class JustEat(_CatalogueOnly):
    id = "just_eat"
    name = "Just Eat (partner)"
    category = "Food delivery"
    cost_type = "paid"
    what_it_does = "Marketplace app, strong for takeaways. Partner sign-up."
    docs_url = "https://restaurants.just-eat.co.uk/"
    status_note = "Catalogue only. Terms not checked today."
