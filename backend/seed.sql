-- shop stock. questions do NOT live here, they come from data/*.csv
-- via load_questions.py.
--
-- safe to run on its own (without reset_db.py, which wipes every account):
-- the upsert on slug means re-running this adds new items and reprices
-- existing ones without touching anybody's inventory, since the ids are kept.
--
-- image_url is which drawing this is, relative to frontend/src/assets/. the
-- frontend imports by slug rather than reading this path - vite content-hashes
-- everything under src/assets, so the built filename isn't knowable here -
-- but it saves anyone having to guess which png a row means.
--
-- three things to keep true or tests/api/test_shop.py breaks:
--   * nothing is free. test_cannot_buy_what_you_cannot_afford gives a user 0
--     coins and expects a 402 on the CHEAPEST item, which a price of 0 would
--     happily sell them.
--   * the cheapest item stays buy-once. test_cannot_buy_twice and the `item`
--     fixture in tests/db/test_queries.py both grab the cheapest row.
--   * at least 4 items, and the catalog stays affordable on 1000 coins
--     (test_coins_never_go_negative buys the lot). this one totals 580.
--
-- grass is deliberately NOT sold: a key with no skin renders grass already,
-- so going back to the default is free rather than a repurchase.

insert into shop_items (slug, name, price, image_url, kind, habitat) values
    ('extra-key',     'Unlock a Key',   50,  'keys/grass_key.png', 'key_unlock', 'land'),

    ('soil-key',      'Soil Key',       60,  'keys/dirt_key.png',        'key_skin',  'land'),
    ('water-key',     'Water Key',      120, 'keys/water_key.png',       'key_skin',  'water'),

    ('pink-daffodil', 'Pink Daffodils', 20,  'shop_items/flower_1.png',  'accessory', 'land'),
    ('blue-daffodil', 'Blue Daffodils', 20,  'shop_items/flower_2.png',  'accessory', 'land'),
    ('pink-daisy',    'Pink Daisies',   25,  'shop_items/flower_3.png',  'accessory', 'land'),
    ('purple-daisy',  'Purple Daisies', 25,  'shop_items/flower_4.png',  'accessory', 'land'),
    ('white-tulip',   'White Tulips',   30,  'shop_items/flower_5.png',  'accessory', 'land'),
    ('blue-tulip',    'Blue Tulips',    30,  'shop_items/flower_6.png',  'accessory', 'land'),
    ('tomato',        'Tomatoes',       40,  'shop_items/veg_1.png',     'accessory', 'land'),
    ('carrot',        'Carrots',        40,  'shop_items/veg_2.png',     'accessory', 'land'),

    ('fish',          'Fish',           80,  'shop_items/fish_1.png',    'accessory', 'water'),
    ('jellyfish',     'Jellyfish',      90,  'shop_items/fish_2.png',    'accessory', 'water')
on conflict (slug) do update set
    name      = excluded.name,
    price     = excluded.price,
    image_url = excluded.image_url,
    kind      = excluded.kind,
    habitat   = excluded.habitat;
