#!/usr/bin/env python3
from card_shuffling_test import CardShufflingDemo

print('Simulating card switching...')
demo = CardShufflingDemo()
print('\nInitial display:')
demo.show_only_current_card()
print('\nSwitch to next card:')
demo.current_card = 1
demo.show_only_current_card()
print('\nSwitch back to first card:')
demo.current_card = 0
demo.show_only_current_card()
print('\nDone')
