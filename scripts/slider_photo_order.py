"""Order card slider photos so each sequence sells the card's promise.

First photo = the single strongest shot for the card's promise, then the story
(venue/boat, food/drinks, views, details). Off-topic shots (menus, payment
graphics, text boards, near-duplicates) are dropped. Orders were picked by
looking at contact sheets of every card, not by filename.

PHOTO_ORDER keys are page -> card number (1-based slider index on the page),
values are 1-based indexes into the card's current photo list. Indexes not
listed are dropped. The same order is applied to every language version that
uses the bpa-slider deck (image files are shared, only alt text differs).
See budapest-adventures scripts/slider_photo_order.py for the same tool.

Usage: python3 scripts/slider_photo_order.py [--check]
"""
import html
import json
import re
import sys
import unicodedata
from pathlib import Path
from urllib.parse import quote, unquote

ROOT = Path(__file__).resolve().parent.parent

PHOTO_ORDER = {
    "dinner-cruises-paris": {
        1: [  # Eiffel Tower through the starlit glass salon; drop printed menu
            "6557d4b0f32b0baf412f95f5",
            "6557d4e025d7640b84b767a7",
            "6557d5481646b713aa9844bb",
            "6557d53788f84266f7d4d3fd",
            "67cd8839027b6113a595e065",
            "67cd88417f149b38ec65a082",
            "65574579abe3f651db5aa05e",
            "6557d4d0ee321d02c1230703",
            "6557d4919c0214cc0fedf303",
        ],
        2: [  # diners in the all-glass salon
            "65b3ca5a10dff95c052a1d66",
            "653e673d95e852a1e22beb62",
            "653d3b4265da31aec38bcf19",
            "653e675abdd0b1ea6c8c9f69",
            "653e67da33c8ccff6d081df9",
            "653d36a284a3efc081aadfc2",
            "653d36c8ae6bc593448e1d73",
            "653d37023b2ad1cc7f526966",
            "653d3b57bdd0b1ea6c8c3823",
            "653e6827827717b4f627f685",
        ],
        3: [  # Eiffel Tower through the window; drop printed menu
            "653ba65a5b17054392216a3a",
            "653ba630e82234d2f83caf60",
            "653ba55cd329e3f304e49528",
            "653babacb83808875bf315cf",
            "653ba50f85071d68a6ddafb1",
            "655a436a800621546ac06548",
            "653babdb3979d1253bd875f6",
            "655a3ae527bb0b39f6c997b5",
            "653babffc1748f0bdc35707e",
        ],
        4: [  # leather club chairs by the river
            "655a4a074cb61f6f2b353166",
            "655a4a64557a0a7fd64d95ac",
            "655a4a48e4202211d7a66a44",
            "655a4a3e6c7b81432a94f5d7",
            "655a4d5ad296ce49e7807854",
            "655a4cc5262466a413c706f0",
            "655a4cde63c9530593bcab5a",
            "655a4d3987a5a72a4044b7fb",
            "655a4ab627bb0b39f6d36351",
            "655a49f2808f61ff15d832e6",
        ],
        5: [  # Eiffel Tower in the violet salon
            "655a5553736359512068fe7b",
            "655a55121de34c4d81517211",
            "655a52c47dbc4d7805270527",
            "655a4e6a63c9530593bda332",
            "655a4e3d52e85fb000e1583c",
            "655a52b2c9af12fd4ac8cd35",
            "655a527b87a5a72a40484e63",
            "655a526ea75bf3251633e6e2",
            "655a4e4aba4706dfb3746386",
            "655a4e5a95abd3458678eb66",
        ],
        6: [  # the boat passing the Eiffel Tower
            "trattoria-2.avif",
            "673aa1a0a6ff68067bee64cc",
            "trattoria-5.avif",
            "trattoria-3.avif",
            "trattoria-4.avif",
            "trattoria-1.avif",
            "trattoria-7.avif",
            "trattoria-6.avif",
        ],
        7: [  # the lit boat on the Seine at dusk
            "fracasse-2.avif",
            "fracasse-1.avif",
            "fracasse-3.avif",
            "673abf57b32cf03625c0afc7",
            "fracasse-4.avif",
            "fracasse-5.avif",
            "fracasse-6.avif",
            "fracasse-7.avif",
        ],
        8: [  # couple toasting at a window table
            "maxims-2.avif",
            "maxims-4.avif",
            "maxims-1.avif",
            "673be6fcb2781534f290995e",
            "maxims-3.avif",
            "maxims-6.avif",
            "maxims-5.avif",
            "maxims-7.avif",
        ],
        9: [  # dining room with the lit Eiffel Tower
            "paris-new-years-eve-cruise-eiffel-croisieres-01.avif",
            "paris-new-years-eve-cruise-eiffel-croisieres-02.avif",
            "eiffel-croisieres-1.avif",
            "eiffel-croisieres-2.avif",
            "eiffel-croisieres-3.avif",
            "eiffel-croisieres-4.avif",
            "eiffel-croisieres-5.avif",
            "eiffel-croisieres-6.avif",
            "paris-new-years-eve-cruise-eiffel-croisieres-03.avif",
        ],
        10: [  # couple toasting with the Eiffel Tower
            "marina-early-2.avif",
            "marina-early-1.avif",
            "673d2204f64c04f3548f3db7",
            "marina-early-3.avif",
            "marina-early-7.avif",
            "marina-early-6.avif",
            "marina-early-5.avif",
            "marina-early-4.avif",
        ],
    },
    "seine-river-cruises-paris": {
        1: [  # full boat at Pont Alexandre III and the Eiffel Tower; drop audio app graphic
            "699480970fd56c513a2749e0",
            "653a414852cb182029292fcf",
            "653a45e0f0af99ac540e8f87",
            "658343456e576281bed9f072",
            "6994809779bbf0286c89e95d",
            "653a4154b89b51259a606e63",
            "653a40c21889f4f91e8b7f7f",
            "699480973bf5a60684dd2a08",
            "653a3feafe9dfc29b0e39b63",
        ],
        2: [  # the boat with a full open deck
            "68cffc9a8866db331e9230e1",
            "65846bb926ba8bc52ad55bb6",
            "65846b42ada659711ad555cf",
            "65885fff646aea108e53644f",
            "65846bce83ac586c23ce5a1c",
            "65846b865ef221fbe4194b58",
            "65846b5e4f5d729443faee76",
            "658477b97c7f37d58f3713b3",
            "65847828699ad476ca060f45",
        ],
        3: [  # the boat on the Seine; drop app sign
            "65848c15b5df26ea46257c3e",
            "65848ac74d92341e4edbaccb",
            "65846e1041aea632d9c84087",
            "65848aa4e3a71b9007bce359",
            "65848ad831b73f6354c18793",
            "65846e603090ee5eab8401bb",
            "65846e4f530a250419def026",
            "65846d81feca5d5213f021ec",
            "65848c7ce80ab66f989795f9",
        ],
        4: [  # Batobus at the pier
            "65848a61b5df26ea46248b7e",
            "65846eb88c5a2cf5f5d605fd",
            "65846edfcc95d8dae2c403b8",
            "65846eea3f11a22478ff96ec",
            "65846f7a272db29b1850cff2",
            "65848a795158aebb4706cacc",
            "65846f9adf4ea88c69a19d99",
            "65848a5109a769f1933f88ea",
        ],
        5: [  # passing through a canal lock
            "658470dd143330e7a2389ab5",
            "65847201987cd15fbf037392",
            "658471238fa08153f6049af5",
            "658470f5b89b0333b19ae37b",
            "658470c86cd6bda23c7c9939",
            "65847050eaee898abb9eee51",
            "6584700dfdab6a60e8c81a36",
            "65847030abacf7fa66feded3",
            "65848a084d804452e10d98a7",
            "65847001bfeeb7fb07e28494",
        ],
        6: [  # champagne on the private boat
            "private-boat-1.avif",
            "private-boat-7.avif",
            "private-boat-3.avif",
            "673eb3fdde1441cad34d0874",
            "private-boat-2.avif",
            "private-boat-6.avif",
            "private-boat-4.avif",
            "private-boat-5.avif",
        ],
        7: [  # waffle with the lit Eiffel Tower
            "waffle-cruise-1.avif",
            "waffle-cruise-2.avif",
            "waffle-cruise-3.avif",
            "waffle-cruise-5.avif",
            "673e9b0b9ee78f1508963a84",
            "waffle-cruise-4.avif",
            "waffle-cruise-6.avif",
            "waffle-cruise-7.avif",
        ],
        8: [  # full boat on the Seine
            "673e9e00bd36163cc4b80098",
            "crepe-cruise-1.avif",
            "crepe-cruise-2.avif",
            "crepe-cruise-3.avif",
            "crepe-cruise-4.avif",
            "crepe-cruise-5.avif",
            "crepe-cruise-7.avif",
            "crepe-cruise-6.avif",
        ],
        9: [  # couple toasting with the Eiffel Tower; drop duplicate salon shot
            "lunch-cruise-1.avif",
            "lunch-cruise-5.avif",
            "673ea880ceb64d8f7b6297c5",
            "lunch-cruise-3.avif",
            "lunch-cruise-4.avif",
            "lunch-cruise-6.avif",
            "lunch-cruise-7.avif",
        ],
        10: [  # family with ice cream at the Eiffel Tower
            "ice-cream-cruise-1.avif",
            "ice-cream-cruise-4.avif",
            "ice-cream-cruise-6.avif",
            "ice-cream-cruise-2.avif",
            "ice-cream-cruise-3.avif",
            "673ea9fc3711fbda1938d41c",
            "ice-cream-cruise-5.avif",
            "ice-cream-cruise-7.avif",
        ],
    },
    "canal-cruises-amsterdam": {
        1: [  # friends with drinks on the open boat; drop logo and payment graphics
            "67f4255df022d8cc14b67320",
            "67f4255848370e313daed8bb",
            "67f4255c46d4db6c6e7caee2",
            "67f425584d341b8d6c7a2a1d",
            "67f4255a09ef380e8068006d",
            "67f42558ad1d23f5dbbbf2fc",
            "67f4255b7551d5a86e3756ea",
            "67f4255b7551d5a86e3756e5",
            "67f425584a10959b400e70f5",
            "659071b66972c22d34c175f8",
            "658f0ecbd7d409840b9ead59",
            "659071d1b807603c1cf56794",
            "658f0ef422d0bb27fea27395",
            "659071299f51f4557ff81e0f",
            "65907135edabb59a89321247",
            "65907161d6b0574d4e83e651",
        ],
        2: [  # canal houses through the glass roof
            "6590725d11f274f3b22830fa",
            "659058cf4b3e0306b4784d9f",
            "659053db4b3e0306b475db5c",
            "659054227ab093299d2b0808",
            "6590728ab807603c1cf5ef6c",
            "659072ab015470c887bdb2a6",
            "6590543242ecf1f76a52f7bf",
            "65905440e6f0cbe17a6c4895",
        ],
        3: [  # Dutch cheese boards on board
            "65905b88582e5f01dc82afc6",
            "6590732a560e9077a3cfbd57",
            "659073740382270a544ddd40",
            "65907341eadc405562beeac8",
            "6590740db807603c1cf6b832",
            "659073db9f51f4557ff9851d",
            "65907319d4ddcb4f4ddeaffe",
        ],
        4: [  # the boat at the pier; drop ticket billboard
            "659054c011f274f3b2193af7",
            "6590744e6cb0602f98864103",
            "659054d5d4ddcb4f4dcf065c",
            "659074a1015470c887bebe3a",
            "65905ba9506b4a66fe02a843",
        ],
        5: [  # open bar with guests
            "659075fa8f4163a153f33119",
            "65907596ff63da989b5a32d2",
            "6590752d64aed4b6f4f35fbb",
            "65905531506b4a66feff2538",
            "65905bc6ff63da989b4d888e",
            "6595158e6bd758cb3a46a4f7",
            "65907614ba48a05dfddde98f",
            "6590551b5ef9355acc5e88cb",
        ],
    },
    "thames-river-cruises-london": {
        1: [  # passengers passing under Tower Bridge; drop 6 duplicates
            "699b08d6c762fd0acc15f8b6",
            "699b059ca38a7cca1a7cf095",
            "699b08d680272ee3fdd3c95f",
            "699b0643b578d621f8123614",
            "699b08d6b087b77b3ced47e9",
            "664c71f2590abfbd6efe6c6f",
            "699b08d65cac23a4d0c9f170",
            "699b08d6f447411e1f63a6f6",
            "699b08d603c92db082bc1e33",
            "699b08d6de2e66a74a0d1e11",
            "664c725764b3594f68fd93f7",
        ],
        2: [  # the boat on the Thames; drop 7 duplicates
            "699b0a8b9bd6f31928b9f10d",
            "699b0a8bb9254eb8704b1bac",
            "699b0a8b93a8c84cff5453ee",
            "699b0a8b5507b105f2f2b45e",
            "699b0a8bd13692179115349e",
            "699b0a8bda08b81d22999b79",
            "699b0a8b04eef17ca5aca349",
            "699b0a8b3bfec501d96b124c",
        ],
        3: [  # full deck facing the London Eye; drop leaflet
            "66bce665c902f1a96e3daac5",
            "665090a8254e388ad43d3d9d",
            "66bce592b195be6031928f32",
            "66bce5a47ef8ec4beb0c7c0a",
            "66bce53cc2632219dd6a17d8",
            "66bce5b5d9e3bdc0804a14f3",
            "66bce5d85aef7d424a6a4382",
            "66bce62596d911fc125504b1",
            "66bce5817a8bc8744d2cfa52",
            "66bce59b7a8bc8744d2d18a8",
            "66bce56673f69e88dc6d3e94",
        ],
        4: [  # speedboat at full spray
            "6650b41798f4d04908729266",
            "66bcca30f894918c1a11e135",
            "66bcca3934030dea499fd006",
            "699b0d065c562be886a0dff5",
            "66bcca702c9db7e52ee7756d",
            "699b0d53a9f8b010baecb972",
            "66bcca532db0296a44864202",
            "699b0d2e64e02743825e1bf1",
            "66bcc8ce46595736f8664bbd",
            "66bcc8da92218f8dd4d1a163",
        ],
        5: [  # London Eye from the RIB
            "66bccce6e2c7c685540de984",
            "66bcccc252d57da192221aa0",
            "66bcccd8b8fc6c29d172da5c",
            "66bcfd6880574d8e5abf73ad",
            "66bcccf5dae908d9d837d457",
        ],
        6: [  # friends at afternoon tea with the view
            "6650b342ba4546b998399ee3",
            "6650b38faf0e85a390beb01d",
            "665092a9bc83b1c78ba71a21",
        ],
    },
    "new-years-eve-cruises-paris": {
        1: [  # couple toasting with the Eiffel Tower
            "paris-new-years-eve-cruise-bateaux-parisiens-01.avif",
            "paris-new-years-eve-cruise-bateaux-parisiens-02.avif",
            "paris-new-years-eve-cruise-bateaux-parisiens-03.avif",
            "paris-new-years-eve-cruise-bateaux-parisiens-04.avif",
            "paris-new-years-eve-cruise-bateaux-parisiens-08.avif",
            "paris-new-years-eve-cruise-bateaux-parisiens-09.avif",
            "paris-new-years-eve-cruise-bateaux-parisiens-05.avif",
            "paris-new-years-eve-cruise-bateaux-parisiens-06.avif",
            "paris-new-years-eve-cruise-bateaux-parisiens-11.avif",
            "paris-new-years-eve-cruise-bateaux-parisiens-07.avif",
            "paris-new-years-eve-cruise-bateaux-parisiens-13.avif",
            "paris-new-years-eve-cruise-bateaux-parisiens-12.avif",
            "paris-new-years-eve-cruise-bateaux-parisiens-14.avif",
            "paris-new-years-eve-cruise-bateaux-parisiens-10.avif",
        ],
        2: [  # friends at dinner with Paris lights
            "paris-new-years-eve-cruise-marina-de-paris-03.avif",
            "paris-new-years-eve-cruise-marina-de-paris-01.avif",
            "paris-new-years-eve-cruise-marina-de-paris-02.avif",
            "paris-new-years-eve-cruise-marina-de-paris-04.avif",
            "paris-new-years-eve-cruise-marina-de-paris-05.avif",
        ],
        3: [  # sparklers at the table
            "paris-new-years-eve-cruise-bateaux-mouches-01.avif",
            "paris-new-years-eve-cruise-bateaux-mouches-06.avif",
            "paris-new-years-eve-cruise-bateaux-mouches-07.avif",
            "paris-new-years-eve-cruise-bateaux-mouches-02.avif",
            "paris-new-years-eve-cruise-bateaux-mouches-05.avif",
            "paris-new-years-eve-cruise-bateaux-mouches-08.avif",
            "paris-new-years-eve-cruise-bateaux-mouches-03.avif",
            "paris-new-years-eve-cruise-bateaux-mouches-04.avif",
            "paris-new-years-eve-cruise-bateaux-mouches-10.avif",
            "paris-new-years-eve-cruise-bateaux-mouches-09.avif",
        ],
        4: [  # Eiffel Tower from the violet dining room
            "paris-new-years-eve-cruise-diamant-bleu-02.avif",
            "paris-new-years-eve-cruise-diamant-bleu-01.avif",
            "paris-new-years-eve-cruise-diamant-bleu-05.avif",
            "paris-new-years-eve-cruise-diamant-bleu-06.avif",
            "paris-new-years-eve-cruise-diamant-bleu-03.avif",
            "paris-new-years-eve-cruise-diamant-bleu-04.avif",
            "paris-new-years-eve-cruise-diamant-bleu-07.avif",
        ],
        5: [  # dining room facing the Eiffel Tower
            "paris-new-years-eve-cruise-eiffel-croisieres-01.avif",
            "paris-new-years-eve-cruise-eiffel-croisieres-02.avif",
            "paris-new-years-eve-cruise-eiffel-croisieres-03.avif",
            "paris-new-years-eve-cruise-eiffel-croisieres-04.avif",
        ],
    },
    "private-cruises-paris": {
        1: [  # champagne with the Eiffel Tower
            "private-seine-cruise-paris-visite-paris-en-bateau-01.avif",
            "private-seine-cruise-paris-visite-paris-en-bateau-08.avif",
            "private-seine-cruise-paris-visite-paris-en-bateau-02.avif",
            "private-seine-cruise-paris-visite-paris-en-bateau-07.avif",
            "private-seine-cruise-paris-visite-paris-en-bateau-04.avif",
            "private-seine-cruise-paris-visite-paris-en-bateau-03.avif",
            "private-seine-cruise-paris-visite-paris-en-bateau-05.avif",
            "private-seine-cruise-paris-visite-paris-en-bateau-06.avif",
        ],
        2: [  # friends with rosé and the Eiffel Tower
            "private-seine-cruise-paris-boat-in-paris-02.avif",
            "private-seine-cruise-paris-boat-in-paris-01.avif",
            "private-seine-cruise-paris-boat-in-paris-04.avif",
            "private-seine-cruise-paris-boat-in-paris-03.avif",
            "private-seine-cruise-paris-boat-in-paris-05.avif",
            "private-seine-cruise-paris-boat-in-paris-06.avif",
            "private-seine-cruise-paris-boat-in-paris-07.avif",
            "private-seine-cruise-paris-boat-in-paris-08.avif",
        ],
        3: [  # couple with champagne
            "private-seine-cruise-paris-myparisriver-01.avif",
            "private-seine-cruise-paris-myparisriver-03.avif",
            "private-seine-cruise-paris-myparisriver-02.avif",
            "private-seine-cruise-paris-myparisriver-04.avif",
            "private-seine-cruise-paris-myparisriver-05.avif",
            "private-seine-cruise-paris-myparisriver-06.avif",
            "private-seine-cruise-paris-myparisriver-07.avif",
        ],
        4: [  # cheering group with the Eiffel Tower
            "private-seine-cruise-paris-jps-boat-02.avif",
            "private-seine-cruise-paris-jps-boat-03.avif",
            "private-seine-cruise-paris-jps-boat-01.avif",
            "private-seine-cruise-paris-jps-boat-05.avif",
            "private-seine-cruise-paris-jps-boat-04.avif",
            "private-seine-cruise-paris-jps-boat-06.avif",
            "private-seine-cruise-paris-jps-boat-07.avif",
            "private-seine-cruise-paris-jps-boat-08.avif",
        ],
        5: [  # Eiffel Tower at sunset selfie
            "private-seine-cruise-paris-paris-water-way-pontoon-01.avif",
            "private-seine-cruise-paris-paris-water-way-pontoon-03.avif",
            "private-seine-cruise-paris-paris-water-way-pontoon-04.avif",
            "private-seine-cruise-paris-paris-water-way-pontoon-06.avif",
            "private-seine-cruise-paris-paris-water-way-pontoon-05.avif",
            "private-seine-cruise-paris-paris-water-way-pontoon-02.avif",
        ],
        6: [  # limousine boat with guests
            "private-seine-cruise-paris-paris-water-way-vip-01.avif",
            "private-seine-cruise-paris-paris-water-way-vip-03.avif",
            "private-seine-cruise-paris-paris-water-way-vip-02.avif",
            "private-seine-cruise-paris-paris-water-way-vip-04.avif",
            "private-seine-cruise-paris-paris-water-way-vip-05.avif",
        ],
    },
    "bateaux-mouches-vs-bateaux-parisiens-dinner-cruise-side-by-side-comparison": {
        1: [  # Eiffel Tower through the starlit salon; drop duplicate starter
            "6557d4b0f32b0baf412f95f5",
            "6557d4e025d7640b84b767a7",
            "6557d7488c95f4ddb81c828e",
            "67cd886c08ea1ae1f6e1c1d9",
            "6557d53788f84266f7d4d3fd",
            "67cd8839027b6113a595e065",
            "67cd88417f149b38ec65a082",
            "67cd881b32f78191cfc0456a",
            "6557d4919c0214cc0fedf303",
            "6557d4d0ee321d02c1230703",
        ],
        2: [  # the lit boat at the Eiffel Tower; drop 2 Bateaux Mouches food shots
            "653d3629ae6bc593448d9b91",
            "653e6797ae6bc5934491f74f",
            "653d3b4265da31aec38bcf19",
            "653e67da33c8ccff6d081df9",
            "653e6827827717b4f627f685",
            "653e675abdd0b1ea6c8c9f69",
            "653d36a284a3efc081aadfc2",
            "653d36c8ae6bc593448e1d73",
            "653d37023b2ad1cc7f526966",
            "653d3b57bdd0b1ea6c8c3823",
        ],
    },
}


SLIDER_RE = re.compile(r'<div[^>]*class="bpa-slider"')
IMG_RE = re.compile(r"<img [^>]*>")
LD_LOG = []
PILL_RE = re.compile(r'(<span class="bpa-pill">1 / )(\d+)(</span>)')


def balanced_end(h, start):
    depth = 0
    for m in re.finditer(r"<(/?)div\b[^>]*>", h[start:]):
        depth += -1 if m.group(1) else 1
        if depth == 0:
            return start + m.end()
    raise ValueError("unbalanced div")


def img_url(im):
    m = re.search(r'data-src="([^"]+)"', im) or re.search(r' src="([^"]+)"', im)
    return m.group(1)


def attr(im, name):
    m = re.search(r'\s%s="[^"]*"' % name, im)
    return m.group(0) if m else None


def fill_slot(template, im):
    """Put photo `im` into the slot `template`.

    Everything that describes the photo (alt, data-cap, srcset, sizes, size)
    stays with the photo. Only the loading mode comes from the slot: the
    first slot loads eagerly with src/srcset, the others lazily with
    data-src/data-srcset behind the slot's placeholder.
    """
    url = img_url(im)
    ss = re.search(r'\s(?:data-)?srcset="([^"]*)"', im)
    ss = ss.group(1) if ss else None
    body = im[len("<img"):].rstrip("/>").rstrip()
    for name in ("src", "data-src", "srcset", "data-srcset", "loading", "fetchpriority", "decoding"):
        body = re.sub(r'\s%s="[^"]*"' % name, "", body)
    slot = "".join(attr(template, n) or "" for n in ("loading", "fetchpriority", "decoding"))
    if 'data-src="' in template:
        ph = re.search(r' src="([^"]*)"', template).group(1)
        media = ' data-src="%s"' % url + (' data-srcset="%s"' % ss if ss else "") + ' src="%s"' % ph
    else:
        media = ' src="%s"' % url + (' srcset="%s"' % ss if ss else "")
    return "<img" + body + slot + media + "/>"


def norm(u):
    """Compare slider URLs (&amp;, spaces) with JSON-LD URLs (%26, %20)."""
    return unquote(html.unescape(u)).lstrip("/")


def ld_url(u, like):
    return ("/" if like.startswith("/") else "") + quote(norm(u), safe="/:()")


def cluster_files(page):
    h = (ROOT / page / "index.html").read_text()
    files = []
    for path, lang in re.findall(
            r'<link href="https://www.thecruisedetective.com/([^"]*)" hreflang="([^"]+)" rel="alternate"', h):
        if lang == "x-default":
            continue
        path = unquote(path)
        for c in (path + ".html", path + "/index.html",
                  unicodedata.normalize("NFD", path) + ".html",
                  unicodedata.normalize("NFD", path) + "/index.html"):
            if (ROOT / c).exists():
                files.append((lang, ROOT / c))
                break
    return files


def photo_key(u):
    """Webflow asset hash when there is one, else the file name."""
    b = norm(u).split("/")[-1]
    m = re.match(r"([0-9a-f]{24})_", b)
    return m.group(1) if m else b


class MissingPhoto(Exception):
    pass


def reorder_page(h, orders):
    sliders = []
    for m in SLIDER_RE.finditer(h):
        sliders.append((m.start(), balanced_end(h, m.start())))
    urls = [[img_url(i) for i in IMG_RE.findall(h[a:b])] for a, b in sliders]
    first_swaps = []
    card_lists = {}
    for idx in sorted(orders, reverse=True):
        order = orders[idx]
        a, b = sliders[idx - 1]
        s = h[a:b]
        imgs = IMG_RE.findall(s)
        by_key = {photo_key(img_url(i)): i for i in imgs}
        new = []
        for k in order:
            if k in by_key:
                new.append(by_key[k])
            elif k.startswith("/assets/") and (ROOT / k.lstrip("/")).exists():
                # a photo added to the card: same alt as the card's other photos
                new.append('<img%s src="%s"/>' % (attr(imgs[0], "alt") or ' alt=""', k))
            else:
                raise MissingPhoto((idx, k))
        card_lists[idx] = ([img_url(i) for i in imgs], [img_url(i) for i in new])
        rest_t = imgs[1] if len(imgs) > 1 else imgs[0]
        tags = [fill_slot(imgs[0], new[0])] + [fill_slot(rest_t, im) for im in new[1:]]
        head = s[:s.find("<img ")]
        tail = s[s.rfind(">", 0, s.rfind("</div>")) + 1:]
        # keep the separator used between tags
        sep = "\n" if "\n<img " in s else ""
        new_s = head + sep.join(tags) + tail
        media = [m.start() for m in re.finditer(r'<div class="bpa-media[" ]', h[max(0, a - 3000):a])]
        pre_start = max(0, a - 3000) + media[-1] if media else a
        pre = h[pre_start:a]
        pre_new, n = PILL_RE.subn(lambda m: m.group(1) + str(len(order)) + m.group(3), pre)
        assert n <= 1
        # the visible caption under the counter starts as the first photo's data-cap
        cap = attr(tags[0], "data-cap")
        cap = cap.split('"')[1] if cap else ""
        pre_new = re.sub(r'(<span class="bpa-cap"[^>]*>)[^<]*(</span>)', lambda m: m.group(1) + cap + m.group(2), pre_new, count=1)
        h = h[:pre_start] + pre_new + new_s + h[b:]
        if img_url(imgs[0]) != img_url(new[0]):
            first_swaps.append((idx, img_url(imgs[0]), img_url(new[0])))
    # JSON-LD: each card's ListItem image (and the Article lead image for card 1)
    # follows the card's first photo. Replace as text to keep the formatting, but
    # only when every occurrence of the old URL sits in one of those spots.
    def fix_ld(m):
        block = m.group(0)
        body = block[block.find(">") + 1:block.rfind("<")]
        try:
            data = json.loads(body)
        except ValueError:
            return block
        nodes = []
        def walk(o):
            if isinstance(o, dict):
                nodes.append(o)
                for v in o.values():
                    walk(v)
            elif isinstance(o, list):
                for v in o:
                    walk(v)
        walk(data)
        def imgs_of(o):
            im = o.get("image")
            if isinstance(im, str):
                return [im]
            if isinstance(im, list):
                return [x for x in im if isinstance(x, str)]
            return []
        def count(lst, u):
            return sum(1 for x in lst if norm(x).endswith(norm(u)))
        for idx, old, new_u in first_swaps:
            allowed = 0
            for n in nodes:
                if n.get("@type") == "ListItem" and n.get("position") == idx and isinstance(n.get("item"), dict):
                    allowed += count(imgs_of(n["item"]), old)
                if idx == 1 and n.get("@type") in ("Article", "BlogPosting", "WebPage"):
                    allowed += count(imgs_of(n), old)
            total = sum(count(imgs_of(n), old) for n in nodes)
            spellings = {x for x in re.findall(r'"([^"]+)"', block)
                         if "/assets/" in x and norm(x).endswith(norm(old))}
            if allowed and allowed == total and sum(block.count('"%s"' % x) for x in spellings) == allowed:
                for x in spellings:
                    block = block.replace('"%s"' % x, '"%s%s"' % (x[:x.find("/assets/")], ld_url(new_u, "/")))
                LD_LOG.append((idx, "ok"))
            elif total:
                LD_LOG.append((idx, "skip: old url also used elsewhere (%d/%d)" % (allowed, total)))
        # Multi-photo image lists made from one card's slider (hostels): follow
        # the new slider order, drop removed photos, lead with the new first photo.
        def fix_list(lm):
            items = re.findall(r'"([^"]*)"', lm.group(2))
            if len(items) < 2:
                return lm.group(0)
            for idx, (old_list, new_list) in card_lists.items():
                old_n = [norm(u) for u in old_list]
                if not all(norm(u) in old_n for u in items):
                    continue
                new_n = [norm(u) for u in new_list]
                kept = sorted([u for u in items if norm(u) in new_n], key=lambda u: new_n.index(norm(u)))
                if not kept or norm(kept[0]) != new_n[0]:
                    kept = [ld_url(new_list[0], items[0])] + kept
                kept = kept[:len(items)]
                if kept == items:
                    return lm.group(0)
                inner = lm.group(2)
                lead = re.match(r'\s*', inner).group(0)
                trail = re.search(r'\s*$', inner).group(0)
                sep = re.search(r'",(\s*)"', inner)
                sep = "," + (sep.group(1) if sep else " ")
                LD_LOG.append((idx, "list reordered"))
                return lm.group(1) + lead + sep.join('"%s"' % u for u in kept) + trail + "]"
            return lm.group(0)
        block = re.sub(r'("image":\s*\[)([^\]]*)\]', fix_list, block)
        return block
    h = re.sub(r'<script[^>]*type="application/ld\+json"[^>]*>.*?</script>', fix_ld, h, flags=re.S)
    return h, urls, first_swaps


def main():
    check = "--check" in sys.argv
    report = {}
    for page, orders in PHOTO_ORDER.items():
        files = cluster_files(page)
        done, skipped = [], []
        for lang, f in files:
            h = f.read_text()
            if 'class="bpa-slider"' not in h:
                skipped.append(lang + " (old w-slider template)")
                continue
            try:
                new_h, urls, _ = reorder_page(h, orders)
            except MissingPhoto as e:
                skipped.append("%s (different photo set: %s)" % (lang, e))
                continue
            if new_h != h:
                if not check:
                    f.write_text(new_h)
                done.append(lang)
        report[page] = {"changed": done, "skipped": skipped}
    print(json.dumps(report, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
