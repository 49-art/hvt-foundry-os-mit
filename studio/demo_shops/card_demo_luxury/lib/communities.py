"""
Community / heritage search templates for "Find for my business".

Hand-written. Each community has English search phrases plus phrases in the
language(s) owners and their suppliers actually use, so the owner finds their
own community's importers and wholesalers, not just the big chains.

{city} is filled with the town name in that language (London forms are below),
{area} with the local area in English (e.g. "Harrow").

Honest note: these phrases were written carefully but have NOT yet been checked
by a native speaker of each language. Each language says so on screen
("checked_by_native_speaker": False). Ask the owner to correct them; their
corrections can be typed straight into the free-text box.
"""
from __future__ import annotations

from typing import Dict, List

CATEGORIES: Dict[str, str] = {
    "suppliers": "Suppliers and wholesalers",
    "stock": "Stock and products",
    "finance": "Money: loans, grants, bank accounts, card machines",
    "delivery": "Delivery and couriers (incl. food delivery apps)",
    "storage": "Storage",
    "other": "Anything else (type it)",
}

RTL = {"ar", "fa", "ur", "ps", "ckb", "prs", "he"}

# English phrases for every community. {adj} = community word ("Romanian"), may be empty.
EN_TEMPLATES: Dict[str, List[str]] = {
    "suppliers": ["{adj} food wholesaler near {area}", "{adj} cash and carry {city}"],
    "stock": ["{adj} products importer UK wholesale", "{adj} grocery distributor UK"],
    "finance": ["small business grant {area} council", "business bank account for a small shop UK",
                "card payment machine small shop UK fees", "Start Up Loans British Business Bank"],
    "delivery": ["same day courier {area}", "parcel delivery for small business UK",
                 "sign up takeaway shop Deliveroo Uber Eats Just Eat {city}"],
    "storage": ["self storage near {area}", "small business storage unit {area}",
                "cold storage rental {city} small business"],
}


def _L(code, name, city, q, dir_=None, checked=False, note=""):
    return {"code": code, "name": name, "dir": dir_ or ("rtl" if code in RTL else "ltr"),
            "city_london": city, "queries": q, "checked_by_native_speaker": checked, "note": note}


COMMUNITIES: List[dict] = [
    {"id": "romanian", "label": "Romanian / Moldovan", "adj": "Romanian",
     "map_regex": "roman|românesc|romanesc|moldov|carpat|transilvan",
     "palette": {"primary": "#002B7F", "accent": "#FCD116", "bg": "#FFF8E7", "text": "#1A1A2E", "name": "Tricolour and ie embroidery"},
     "langs": [_L("ro", "Romanian", "Londra", {
         "suppliers": ["angro produse românești {city}", "distribuitor produse românești Marea Britanie"],
         "stock": ["import produse alimentare românești Marea Britanie", "furnizor produse românești pentru magazin {city}"],
         "finance": ["cont bancar pentru firmă în Marea Britanie", "împrumut pentru afaceri mici Marea Britanie"],
         "delivery": ["firmă de curierat colete România Anglia", "curier colete {city}"],
         "storage": ["depozit de închiriat {city}"],
     })]},
    {"id": "polish", "label": "Polish", "adj": "Polish",
     "map_regex": "polsk|polish|polski|polska|delikatesy",
     "palette": {"primary": "#B5122B", "accent": "#F2C14E", "bg": "#FFF4F0", "text": "#2A0A10", "name": "Crimson and wycinanki colours"},
     "langs": [_L("pl", "Polish", "Londyn", {
         "suppliers": ["hurtownia polska żywność {city}", "polski dystrybutor żywności Wielka Brytania"],
         "stock": ["polskie produkty hurt Wielka Brytania", "dostawca polskich produktów do sklepu {city}"],
         "finance": ["konto firmowe w Wielkiej Brytanii", "pożyczka dla małej firmy Wielka Brytania"],
         "delivery": ["firma kurierska paczki Polska Anglia", "kurier przesyłki {city}"],
         "storage": ["magazyn do wynajęcia {city}"],
     })]},
    {"id": "arabic", "label": "Arabic (Middle Eastern / North African)", "adj": "Middle Eastern",
     "map_regex": "arab|leban|syria|shami|damas|iraq|egypt|moroc|maghreb|yemen|palestin|jordan|halal|baghdad|beirut",
     "palette": {"primary": "#0B5D3B", "accent": "#C9A227", "bg": "#FBF6EA", "text": "#1E1B12", "name": "Emerald and gold"},
     "en_extra": {"finance": ["Islamic business finance UK", "sharia compliant business bank account UK"],
                  "suppliers": ["halal food wholesaler {city}", "Arabic sweets wholesale supplier UK"]},
     "langs": [_L("ar", "Arabic", "لندن", {
         "suppliers": ["مورد جملة مواد غذائية عربية {city}", "تاجر جملة منتجات حلال {city}"],
         "stock": ["استيراد منتجات غذائية عربية بريطانيا", "موزع حلويات عربية بريطانيا"],
         "finance": ["تمويل إسلامي للشركات الصغيرة بريطانيا", "فتح حساب بنكي تجاري في بريطانيا"],
         "delivery": ["شركة شحن طرود من بريطانيا", "توصيل طلبات للمطاعم {city}"],
         "storage": ["مستودع للإيجار {city}"],
     })]},
    {"id": "turkish", "label": "Turkish", "adj": "Turkish",
     "map_regex": "turk|türk|anatol|istanbul|ankara|izmir|efes|ocakbasi|ocakbaşı",
     "palette": {"primary": "#C8102E", "accent": "#1FA6A0", "bg": "#FFF5EE", "text": "#231A1A", "name": "Red and İznik turquoise"},
     "en_extra": {"suppliers": ["Turkish food wholesaler north London"]},
     "langs": [_L("tr", "Turkish", "Londra", {
         "suppliers": ["Türk gıda toptancısı {city}", "Türk ürünleri toptan dağıtıcı İngiltere"],
         "stock": ["Türk ürünleri ithalatçısı İngiltere", "market için Türk ürünleri tedarikçisi {city}"],
         "finance": ["İngiltere'de küçük işletme kredisi", "İngiltere'de şirket banka hesabı açma"],
         "delivery": ["Türkiye'ye kargo gönderimi {city}", "kurye firması {city}"],
         "storage": ["depo kiralama {city}"],
     })]},
    {"id": "kurdish", "label": "Kurdish", "adj": "Kurdish",
     "map_regex": "kurd|kurdistan|erbil|hewler|amed|mezopotamya|mesopotam",
     "palette": {"primary": "#278E43", "accent": "#FEBD11", "bg": "#FFF9EC", "text": "#1C1C1C", "name": "Green, red and sun gold"},
     "langs": [
         _L("kmr", "Kurdish (Kurmanji)", "Londonê", {
             "suppliers": ["firoşgeha xwarinên kurdî {city}", "xwarinên kurdî firotina bi kom {city}"],
             "stock": ["berhemên kurdî {city}"],
         }, note="Many Kurdish shop owners from Turkey also search in Turkish; the Turkish phrases are added too."),
         _L("ckb", "Kurdish (Sorani)", "لەندەن", {
             "suppliers": ["فرۆشگای خواردنی کوردی {city}", "فرۆشتنی کۆ خواردنی کوردی {city}"],
             "stock": ["بەرهەمی کوردی {city}"],
         }),
         _L("tr", "Turkish", "Londra", {
             "suppliers": ["Türk gıda toptancısı {city}"],
             "stock": ["Türk ürünleri ithalatçısı İngiltere"],
         }),
     ]},
    {"id": "south_asian", "label": "South Asian (Indian, Pakistani, Bangladeshi, Sri Lankan Tamil)", "adj": "Asian",
     "map_regex": "indian|india|pakistan|bangla|bengal|lanka|tamil|punjab|desi|spice|masala|bazaar|halal|sweet ?centre|sweet ?mart",
     "palette": {"primary": "#B3005E", "accent": "#FF9933", "bg": "#FFF6E9", "text": "#2B1020", "name": "Magenta and saffron"},
     "en_extra": {"suppliers": ["Indian grocery wholesaler {city}", "Pakistani food wholesaler UK", "Bangladeshi fish importer UK",
                                "Sri Lankan food wholesaler {city}"],
                  "finance": ["Islamic business finance UK"]},
     "langs": [
         _L("hi", "Hindi", "लंदन", {"suppliers": ["भारतीय किराना थोक विक्रेता {city}"], "stock": ["भारतीय मसाले थोक आपूर्तिकर्ता यूके"]}),
         _L("ur", "Urdu", "لندن", {"suppliers": ["پاکستانی کریانہ ہول سیل {city}"], "stock": ["حلال گوشت ہول سیل سپلائر {city}"]}),
         _L("bn", "Bengali", "লন্ডন", {"suppliers": ["বাংলাদেশি মুদি পাইকারি {city}"], "stock": ["বাংলাদেশি মাছ আমদানিকারক যুক্তরাজ্য"]}),
         _L("ta", "Tamil", "லண்டன்", {"suppliers": ["இலங்கை உணவுப் பொருட்கள் மொத்த விற்பனை {city}"], "stock": ["தமிழ் கடை மொத்த விநியோகஸ்தர் {city}"]}),
         _L("pa", "Punjabi (Gurmukhi)", "ਲੰਡਨ", {"suppliers": ["ਭਾਰਤੀ ਕਰਿਆਨਾ ਥੋਕ ਵਿਕਰੇਤਾ {city}"]}),
     ]},
    {"id": "caribbean", "label": "Caribbean", "adj": "Caribbean",
     "map_regex": "caribbean|jamaica|trinidad|barbad|west ?indian|island|yard|jerk|guyan",
     "palette": {"primary": "#007A3D", "accent": "#FFCD00", "bg": "#F4FBF2", "text": "#111111", "name": "Green, gold and black"},
     "en_extra": {"suppliers": ["Jamaican food importer UK", "West Indian grocery cash and carry {city}"]},
     "langs": [], "lang_note": "Most Caribbean suppliers trade in English, so English phrases are used."},
    {"id": "west_african", "label": "West African (Nigerian, Ghanaian, Sierra Leonean, Senegalese…)", "adj": "African",
     "map_regex": "africa|nigeria|ghana|naija|lagos|accra|sierra|senegal|afro|yoruba|jollof",
     "palette": {"primary": "#E4A11B", "accent": "#0F7B3F", "bg": "#FFF8E6", "text": "#1B1B1B", "name": "Kente gold and green"},
     "en_extra": {"suppliers": ["Nigerian food wholesaler UK", "Ghanaian food importer {city}"]},
     "langs": [_L("fr", "French (francophone West Africa)", "Londres", {
         "suppliers": ["grossiste produits alimentaires africains {city}"],
         "stock": ["importateur produits africains Royaume-Uni"],
     })]},
    {"id": "east_african", "label": "East African / Somali (Somali, Ethiopian, Eritrean)", "adj": "Somali",
     "map_regex": "somal|ethiop|eritre|habesha|addis|mogadish|hargeis|east ?africa|halal",
     "palette": {"primary": "#4189DD", "accent": "#F2A900", "bg": "#F2F7FD", "text": "#10223A", "name": "Sky blue and amber"},
     "en_extra": {"suppliers": ["Somali food wholesaler {city}", "Ethiopian Eritrean food importer UK", "halal meat wholesaler {area}"]},
     "langs": [
         _L("so", "Somali", "London", {"suppliers": ["cunto Soomaali jumlo {city}", "dukaan jumlo ah {city}"]}),
         _L("am", "Amharic", "ለንደን", {"suppliers": ["የኢትዮጵያ ምግብ ጅምላ አከፋፋይ {city}"]}),
     ]},
    {"id": "chinese", "label": "Chinese", "adj": "Chinese",
     "map_regex": "chinese|china|oriental|asia|wing|hong|dragon|panda|golden|jade",
     "palette": {"primary": "#B22222", "accent": "#E8B923", "bg": "#FFF7EC", "text": "#2A1208", "name": "Red lacquer and gold"},
     "en_extra": {"suppliers": ["Chinese supermarket wholesaler {city}", "oriental food cash and carry UK"]},
     "langs": [_L("zh", "Chinese (Simplified)", "伦敦", {
         "suppliers": ["{city} 中国食品批发", "英国 华人超市 供应商"],
         "stock": ["英国 中国食品 进口商"],
         "finance": ["英国 小企业 贷款"],
         "delivery": ["英国 华人 物流 快递"],
         "storage": ["{city} 仓库 出租"],
     })]},
    {"id": "portuguese_brazilian", "label": "Portuguese / Brazilian", "adj": "Portuguese",
     "map_regex": "portug|brasil|brazil|lisbo|madeira|minas|bacalhau",
     "palette": {"primary": "#006847", "accent": "#DA291C", "bg": "#F5FAF7", "text": "#10231B", "name": "Green, red and azulejo"},
     "en_extra": {"suppliers": ["Brazilian food wholesaler UK"]},
     "langs": [_L("pt", "Portuguese", "Londres", {
         "suppliers": ["distribuidor de produtos brasileiros {city}", "grossista de produtos portugueses Reino Unido"],
         "stock": ["importador de produtos brasileiros Reino Unido"],
         "finance": ["conta bancária empresarial no Reino Unido"],
         "delivery": ["envio de encomendas Brasil Reino Unido"],
         "storage": ["armazém para alugar {city}"],
     })]},
    {"id": "bulgarian", "label": "Bulgarian", "adj": "Bulgarian",
     "map_regex": "bulgar|българ|sofia|balkan",
     "palette": {"primary": "#00966E", "accent": "#D62612", "bg": "#FBF8F1", "text": "#1B1B1B", "name": "Green and red on cream"},
     "langs": [_L("bg", "Bulgarian", "Лондон", {
         "suppliers": ["български продукти на едро {city}", "вносител на български храни Великобритания"],
         "delivery": ["куриер пратки България Англия"],
         "storage": ["склад под наем {city}"],
     })]},
    {"id": "lithuanian", "label": "Lithuanian", "adj": "Lithuanian",
     "map_regex": "lietuv|lithuan|baltic|vilnius",
     "palette": {"primary": "#006A44", "accent": "#FDB913", "bg": "#FFFBEF", "text": "#1A1A1A", "name": "Yellow, green and red"},
     "langs": [_L("lt", "Lithuanian", "Londone", {
         "suppliers": ["lietuviškų maisto produktų didmeninė prekyba {city}", "lietuviškų produktų tiekėjas Didžiojoje Britanijoje"],
         "delivery": ["siuntos iš Lietuvos į Angliją"],
         "storage": ["sandėlio nuoma {city}"],
     })]},
    {"id": "ukrainian", "label": "Ukrainian", "adj": "Ukrainian",
     "map_regex": "ukrain|україн|kyiv|kiev",
     "palette": {"primary": "#0057B7", "accent": "#FFD700", "bg": "#F3F7FD", "text": "#0E1A2B", "name": "Blue and wheat gold"},
     "langs": [_L("uk", "Ukrainian", "Лондон", {
         "suppliers": ["українські продукти оптом {city}", "постачальник українських продуктів Велика Британія"],
         "delivery": ["доставка посилок Україна Англія"],
         "storage": ["оренда складу {city}"],
     })]},
    {"id": "greek_cypriot", "label": "Greek / Cypriot", "adj": "Greek",
     "map_regex": "greek|greece|cypr|hellen|olymp|athen|ellas|kypros",
     "palette": {"primary": "#0D5EAF", "accent": "#E8C07D", "bg": "#F4F8FC", "text": "#0B1E33", "name": "Aegean blue and sand"},
     "en_extra": {"suppliers": ["Cypriot food wholesaler {city}"]},
     "langs": [_L("el", "Greek", "Λονδίνο", {
         "suppliers": ["χονδρική ελληνικά προϊόντα {city}", "κυπριακά προϊόντα χονδρική {city}"],
         "stock": ["εισαγωγέας ελληνικών τροφίμων Ηνωμένο Βασίλειο"],
     })]},
    {"id": "afghan", "label": "Afghan", "adj": "Afghan",
     "map_regex": "afghan|kabul|kandahar|herat|ariana|khorasan|halal",
     "palette": {"primary": "#1B1B1B", "accent": "#D32011", "bg": "#FBF5EC", "text": "#1B1B1B", "name": "Black, red and green"},
     "en_extra": {"suppliers": ["Afghan food wholesaler UK", "halal meat wholesaler {area}"],
                  "finance": ["Islamic business finance UK"]},
     "langs": [
         _L("prs", "Dari", "لندن", {"suppliers": ["عمده فروشی مواد غذایی افغانی {city}"]}),
         _L("ps", "Pashto", "لندن", {"suppliers": ["د افغاني خوړو عمده پلورونکی {city}"]}),
     ]},
    {"id": "iranian", "label": "Iranian", "adj": "Persian",
     "map_regex": "iran|persia|parsi|tehran|shiraz|tabriz|isfahan|ferdows",
     "palette": {"primary": "#1C6E8C", "accent": "#E0A526", "bg": "#F6F4EC", "text": "#14222B", "name": "Lapis, turquoise and saffron"},
     "langs": [_L("fa", "Farsi (Persian)", "لندن", {
         "suppliers": ["عمده فروشی مواد غذایی ایرانی {city}", "فروشگاه ایرانی {city}"],
         "stock": ["واردکننده محصولات ایرانی انگلستان"],
     })]},
    {"id": "other", "label": "Other / not listed", "adj": "", "map_regex": "",
     "palette": {"primary": "#3D2C8D", "accent": "#F29E4C", "bg": "#FAF6F0", "text": "#1C1433", "name": "Plum and apricot"},
     "langs": [], "lang_note": "Type the owner's own words (in any language) into the free-text box."},
]

BY_ID = {c["id"]: c for c in COMMUNITIES}


def _clean(s: str) -> str:
    return " ".join(s.split())


def build_queries(community_id: str, category: str, area: str = "London", in_london: bool = True,
                  free_text: str = "") -> List[dict]:
    """Return the list of search phrases, each tagged with its language."""
    if category not in CATEGORIES:
        raise ValueError(f"Unknown category {category!r}")
    c = BY_ID.get(community_id or "other", BY_ID["other"])
    city_en = "London" if in_london else (area or "UK")
    area = area or city_en
    out: List[dict] = []

    def add(q, code, name, direction="ltr", checked=True):
        q = _clean(q)
        if q and q not in [x["q"] for x in out]:
            out.append({"q": q, "lang": code, "lang_name": name, "dir": direction,
                        "checked_by_native_speaker": checked})

    if category != "other":
        for t in EN_TEMPLATES[category]:
            add(t.format(adj=c["adj"], area=area, city=city_en), "en", "English")
        for t in c.get("en_extra", {}).get(category, []):
            add(t.format(area=area, city=city_en), "en", "English")
        for L in c["langs"]:
            city = L["city_london"] if in_london else area
            for t in L["queries"].get(category, []):
                add(t.format(city=city), L["code"], L["name"], L["dir"], L["checked_by_native_speaker"])
    if free_text.strip():
        add(f"{free_text.strip()} {area}", "as typed", "Owner's own words")
        if c["adj"] and category == "other":
            add(f"{c['adj']} {free_text.strip()} UK", "en", "English")
    return out


def palettes() -> List[dict]:
    return [dict(c["palette"], community=c["id"], label=c["label"]) for c in COMMUNITIES]
