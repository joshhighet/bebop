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
    "harvesting frozen peas...",
    "yes, father. i shall become a bat...",
    "may the force be with you...",
    "better out than in, i always say...",
    "E.T. phone home...",
    "just keep swimming...",
    "to infinity and beyond!",
    "gathering moon rocks...",
    "organizing the penguin parade...",
    "initializing the flux capacitor...",
    "calibrating the sonic screwdriver...",
    "unleashing the kraken...",
    "initiating protocol 42...",
    "defragging the hyperspace drive..."
]

bars = [
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
        print(bars[i % len(bars)], end="\r")
        time.sleep(.03)
        i += 1
    print()
