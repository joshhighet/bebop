#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time
import random
phrases = [
    "charging the lazers...",
    "shopping for onions...",
    "making a sandwich...",
    "loading the dishwasher...",
    "decombobulating the capacitor...",
    "angering the bees...",
    "rounding up the usual suspects...",
    "checking the oil...",
    "harvesting frozen peas..."
]

bar = [
    " [=                                                                ]",
    " [    =                                                            ]",
    " [         =                                                       ]",
    " [              =                                                  ]",
    " [                   =                                             ]",
    " [                        =                                        ]",
    " [                             =                                   ]",
    " [                                  =                              ]",
    " [                                       =                         ]",
    " [                                            =                    ]",
    " [                                                 =               ]",
    " [                                                      =          ]",
    " [                                                           =     ]",
    " [                                                                =]"
]

def prints():
    i = 0
    beep = random.choice(phrases)
    middle = int((68 - len(beep)) / 2)
    print(" " * middle + beep)
    for i in range(28):
        print(bar[i % len(bar)], end="\r")
        time.sleep(.03)
        i += 1
    print()