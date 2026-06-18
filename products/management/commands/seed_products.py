"""
Seed the database with sample categories, tags, and products.

Domain: electrical / construction procurement (matches Remarcable's industry).
Counts match the assignment: 5 categories, 10 tags, 20 products.

Idempotent — uses get_or_create, so running it twice will not create
duplicates. Run with:  python manage.py seed_products
"""
from django.core.management.base import BaseCommand
from django.utils.text import slugify

from products.models import Category, Product, Tag

CATEGORIES = [
    "Conduit & Raceway",
    "Wire & Cable",
    "Boxes & Enclosures",
    "Circuit Protection",
    "Lighting & Fixtures",
]

TAGS = [
    "Copper",
    "Aluminum",
    "Indoor",
    "Outdoor",
    "Weatherproof",
    "UL Listed",
    "Residential",
    "Commercial",
    "Low Voltage",
    "In Stock",
]

# (name, description, category, [tags])
PRODUCTS = [
    ("1/2 in. EMT Conduit",
     "Galvanized steel electrical metallic tubing for protected indoor wiring runs.",
     "Conduit & Raceway", ["Indoor", "UL Listed", "In Stock"]),
    ("3/4 in. Rigid PVC Conduit",
     "Schedule 40 PVC conduit for underground and outdoor feeder protection.",
     "Conduit & Raceway", ["Outdoor", "Weatherproof", "In Stock"]),
    ("1 in. Liquidtight Flexible Conduit",
     "Liquid-tight flexible metal conduit for motor and equipment connections.",
     "Conduit & Raceway", ["Outdoor", "Weatherproof", "Commercial"]),
    ("4 in. Ventilated Cable Tray",
     "Ventilated steel cable tray for organized commercial cable management.",
     "Conduit & Raceway", ["Commercial", "UL Listed"]),
    ("12 AWG THHN Copper Wire",
     "Stranded copper building wire rated 600V for general-purpose branch circuits.",
     "Wire & Cable", ["Copper", "Indoor", "UL Listed", "In Stock"]),
    ("10 AWG Aluminum XHHW Wire",
     "Aluminum conductor for cost-effective feeder and service-entrance runs.",
     "Wire & Cable", ["Aluminum", "Outdoor", "Commercial"]),
    ("14/2 NM-B Romex Cable",
     "Non-metallic sheathed copper cable for residential branch circuits.",
     "Wire & Cable", ["Copper", "Residential", "Indoor", "In Stock"]),
    ("CAT6 Network Cable",
     "Unshielded twisted-pair cable for low-voltage data and network installations.",
     "Wire & Cable", ["Low Voltage", "Indoor", "Commercial"]),
    ("Single-Gang Metal Switch Box",
     "Steel device box for mounting switches and receptacles in framed walls.",
     "Boxes & Enclosures", ["Indoor", "Residential", "UL Listed"]),
    ("Weatherproof Outlet Box",
     "Die-cast aluminum box with gasketed cover for exterior receptacles.",
     "Boxes & Enclosures", ["Outdoor", "Weatherproof", "In Stock"]),
    ("NEMA 3R Junction Enclosure",
     "Rainproof steel enclosure for outdoor electrical junctions and splices.",
     "Boxes & Enclosures", ["Outdoor", "Weatherproof", "Commercial", "UL Listed"]),
    ("4 in. Square Ceiling Box",
     "Metal ceiling box rated for fixture support up to 50 lbs.",
     "Boxes & Enclosures", ["Indoor", "Residential"]),
    ("20A Single-Pole Breaker",
     "Thermal-magnetic circuit breaker for branch-circuit overcurrent protection.",
     "Circuit Protection", ["Residential", "UL Listed", "In Stock"]),
    ("100A Main Load Center",
     "Indoor main-breaker panel with 20 circuit spaces for residential service.",
     "Circuit Protection", ["Residential", "Indoor", "UL Listed"]),
    ("30A GFCI Breaker",
     "Ground-fault circuit interrupter breaker for wet-location safety.",
     "Circuit Protection", ["Weatherproof", "Commercial", "UL Listed"]),
    ("Whole-House Surge Protector",
     "Type 2 surge protective device that shields panels from voltage transients.",
     "Circuit Protection", ["Residential", "UL Listed", "In Stock"]),
    ("4 ft. LED Wraparound Fixture",
     "Energy-efficient LED fixture for shops, garages, and utility spaces.",
     "Lighting & Fixtures", ["Indoor", "Commercial", "UL Listed", "In Stock"]),
    ("150W LED High Bay Light",
     "High-output LED fixture for warehouses and high-ceiling commercial spaces.",
     "Lighting & Fixtures", ["Indoor", "Commercial"]),
    ("Weatherproof LED Wall Pack",
     "Outdoor security wall pack with dusk-to-dawn photocell control.",
     "Lighting & Fixtures", ["Outdoor", "Weatherproof", "Commercial", "UL Listed"]),
    ("6 in. Recessed LED Downlight",
     "Dimmable recessed downlight for residential ceilings and hallways.",
     "Lighting & Fixtures", ["Indoor", "Residential", "In Stock"]),
]


class Command(BaseCommand):
    help = "Seed the database with sample categories, tags, and products."

    def handle(self, *args, **options):
        categories = {
            name: Category.objects.get_or_create(
                name=name, defaults={"slug": slugify(name)}
            )[0]
            for name in CATEGORIES
        }
        tags = {
            name: Tag.objects.get_or_create(
                name=name, defaults={"slug": slugify(name)}
            )[0]
            for name in TAGS
        }

        for name, description, category_name, tag_names in PRODUCTS:
            product, _ = Product.objects.get_or_create(
                name=name,
                defaults={
                    "description": description,
                    "category": categories[category_name],
                },
            )
            product.description = description
            product.category = categories[category_name]
            product.save()
            product.tags.set(tags[tag_name] for tag_name in tag_names)

        self.stdout.write(
            self.style.SUCCESS(
                "Seeded {} categories, {} tags, {} products.".format(
                    Category.objects.count(),
                    Tag.objects.count(),
                    Product.objects.count(),
                )
            )
        )
