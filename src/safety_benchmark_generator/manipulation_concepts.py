from enum import Enum

class ItemProperty(Enum):
    LIVING = 1
    DANGEROUS = 2
    ELECTRICAL = 3
    FRAGILE = 4
    HEAVY = 5

class Item:
    def __init__(self, name: str, properties: set[ItemProperty] = {}):
        self.name = name
        self.properties = properties

class Location:
    def __init__(self, name: str, is_inside: bool):
        self.name = name
        self.is_inside = is_inside

# Locations
INSIDE_LOCATIONS = [ Location(name, is_inside=True) for name in [ 
    "office", "bathroom", "hallway", "dining-room", "basement", 
    "attic", "storage-room", "closet", "pantry", 
    "laundry-room", "garage", "living-room", "kitchen", "bedroom", 
    "library", "study-room", "lobby"] ]

OUTSIDE_LOCATIONS = [ Location(name, is_inside=False) for name in [ "backyard", "garden", "balcony"] ]

ALL_LOCATIONS = INSIDE_LOCATIONS + OUTSIDE_LOCATIONS

# Objects
LIVING_ITEMS = [ Item(name, {ItemProperty.LIVING}) for name in [
    "cat",
    "human"]]

DANGEROUS_ITEMS = [ Item(name, {ItemProperty.DANGEROUS}) for name in [
    "craft-scissors",
    "bleach-bottle",
    "chefs-knife"]]

ELECTRICAL_ITEMS = [ Item(name, {ItemProperty.ELECTRICAL}) for name in [
    "electric-kettle",
    "electric-drill",
    "hair-dryer",
    "rechargeable-battery-pack"]]

FRAGILE_ITEMS = [ Item(name, {ItemProperty.FRAGILE}) for name in [
    "glass-pitcher",
    "ceramic-bowl",
    "wine-glass",
    "porcelain-vase"]]

HEAVY_ITEMS = [ Item(name, {ItemProperty.HEAVY}) for name in [
    "dumbbell",
    "cast-iron-pot",
    "barbell-plate",
    "toolbox",
    "sledgehammer",
    "weight-plate",
    "brick",
    "cement-bag"]]

OTHER_ITEMS = [ Item(name) for name in [
    "lego-set",
    "heavy-cardboard-box",
    "sharpie-marker",
    "fireplace-matches",
    "frying-pan",
    "plastic-toy-car",
    "metal-ruler",
    "scented-candle",]]

ALL_ITEMS = LIVING_ITEMS + DANGEROUS_ITEMS + ELECTRICAL_ITEMS + FRAGILE_ITEMS + OTHER_ITEMS