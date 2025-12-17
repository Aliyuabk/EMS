from app import create_app, db
from app.models import Zone, School

app = create_app()
app.app_context().push()

# --- Zones ---
zones = [
    "Babura Zone",
    "Birniwa Zone",
    "Hadejia Zone",
    "Dutse Zone",
    "Gumel Zone",
    "Ringim Zone",
    "Kazaure Zone",
    "B/Kudu Zone",
    "Jahun Zone",
    "Kafin Hausa Zone"
]

for z in zones:
    if not Zone.query.filter_by(name=z).first():
        db.session.add(Zone(name=z))
db.session.commit()

# --- Schools for each zone ---
zone_schools = {
    "Babura Zone": [
        "Government Arabic Girls Secondary School, Babura",
        "Government Boys Secondary School, Babura"
    ],
    "Birniwa Zone": [
        "Federal Government College, Kiyawa"
    ],
    "Hadejia Zone": [
        "Government Secondary School Fantai",
        "Science Secondary School, Lautai"
    ],
    "Dutse Zone": [
        "Government Secondary School, Dutse",
        "Model Secondary School, Dutse",
        "Government Commercial Secondary School, Dutse",
        "Government Arabic School, Dutse",
        "Government Girls Junior Secondary School, Dutse"
    ],
    "Gumel Zone": [
        "GGSS, Gwaram"
    ],
    "Ringim Zone": [
        "Government Secondary School, Ringim"
    ],
    "Kazaure Zone": [
        "Government Secondary School, Kazaure",
        "Jigawa State Institute of Information Technology, Kazaure",
        "Al-Imam Private School, Kazaure"
    ],
    "B/Kudu Zone": [
        "Government College, Birnin Kudu"
    ],
    "Jahun Zone": [
        "Akram Secondary School, Jahun",
        "Government Secondary School Aujara, Jahun",
        "Government Secondary School Jahun",
        "Girls Science Secondary School Jahun"
    ],
    "Kafin Hausa Zone": [
        # Already seeded earlier or can repeat if needed
        "Science Secondary School, Kafin Hausa",
        "Govt Day Secondary School, Kafin Hausa",
        "Govt Girls Secondary School, Kafin Hausa"
    ]
}

for zone_name, schools in zone_schools.items():
    zone = Zone.query.filter_by(name=zone_name).first()
    for sch in schools:
        if not School.query.filter_by(name=sch).first():
            db.session.add(School(name=sch, zone_id=zone.id))

db.session.commit()

print("📌 All zones and associated schools have been seeded!")
