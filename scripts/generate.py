import numpy as np
import random
import json
from PIL import Image


IMAGE_SIZE = (24, 24)
IMAGE_MODE = 'RGBA'

TOTAL_ZOMBITS = 10_000

skin_attributes = [
    # Name         # Primary, secondary, tertiary, and outline RGB values       # Rarity weight
    ('Light Skin', ((108, 184, 50), (60, 136, 2), (76, 152, 18), (34, 32, 52)), 20),
    ('Dark Skin', ((104, 110, 70), (80, 84, 54), (48, 52, 22), (34, 32, 52)), 18),
    ('Pale Skin', ((204, 204, 119), (170, 170, 85), (136, 136, 68), (34, 32, 52)), 10),
    ('Alien', ((255, 0, 180), (208, 32, 156), (229, 21, 167), (34, 32, 52)), 5),
    ('Void', ((34, 32, 52), (27, 24, 153), (36, 33, 204), (44, 41, 255)), 1)
]

suit_attributes = [
    # Name         # Image                                                            # Rarity weight
    ('Black Suit', Image.open('Attributes/Suits/Black_Suit.png').convert(IMAGE_MODE), 5),
    ('Brown Suit', Image.open('Attributes/Suits/Brown_Suit.png').convert(IMAGE_MODE), 5),
    ('Green Suit', Image.open('Attributes/Suits/Green_Suit.png').convert(IMAGE_MODE), 4),
    ('White Suit', Image.open('Attributes/Suits/White_Suit.png').convert(IMAGE_MODE), 4),
    ('Purple Suit', Image.open('Attributes/Suits/Purple_Suit.png').convert(IMAGE_MODE), 4),
    ('NoSuit', Image.new(IMAGE_MODE, IMAGE_SIZE), 2),
    ('Red Suit', Image.open('Attributes/Suits/Red_Suit.png').convert(IMAGE_MODE), 2),
    ('Cardano Suit', Image.open('Attributes/Suits/Cardano_Suit.png').convert(IMAGE_MODE), 1)
]

mouth_attributes = [
    # Name   # Image                            # Rarity weight
    ('NoMouth', Image.new(IMAGE_MODE, IMAGE_SIZE), 10),
    ('Mouth', Image.open('Attributes/Mouths/Mouth.png').convert(IMAGE_MODE), 10),
    ('Long White Beard', Image.open('Attributes/Mouths/Long_White_Beard.png').convert(IMAGE_MODE), 5),
    ('Long Purple Beard', Image.open('Attributes/Mouths/Long_Purple_Beard.png').convert(IMAGE_MODE), 5),
    ('Blonde Beard', Image.open('Attributes/Mouths/Blonde_Beard.png').convert(IMAGE_MODE), 5),
    ('Brown Beard', Image.open('Attributes/Mouths/Brown_Beard.png').convert(IMAGE_MODE), 5),
    ('Red Goatee', Image.open('Attributes/Mouths/Red_Goatee.png').convert(IMAGE_MODE), 5),
    ('Black Goatee', Image.open('Attributes/Mouths/Black_Goatee.png').convert(IMAGE_MODE), 5),
    ('Tusks', Image.open('Attributes/Mouths/Tusks.png').convert(IMAGE_MODE), 2),
    ('Tentacles', Image.open('Attributes/Mouths/Tentacles.png').convert(IMAGE_MODE), 2),
    ('Big Lips', Image.open('Attributes/Mouths/Big_Lips.png').convert(IMAGE_MODE), 2),
    ('Snout', Image.open('Attributes/Mouths/Snout.png').convert(IMAGE_MODE), 2),
    ('Fangs', Image.open('Attributes/Mouths/Fangs.png').convert(IMAGE_MODE), 2),
    ('Creeper Mouth', Image.open('Attributes/Mouths/Creeper_Mouth.png').convert(IMAGE_MODE), 2),
    ('Blunt', Image.open('Attributes/Mouths/Blunt.png').convert(IMAGE_MODE), 2),
    ('Teeth', Image.open('Attributes/Mouths/Teeth.png').convert(IMAGE_MODE), 1)
]

eye_attributes = [
    # Name         # Image                                                           # Rarity weight
    ('Black Eyes', Image.open('Attributes/Eyes/Black_Eyes.png').convert(IMAGE_MODE), 6),
    ('White Eyes', Image.open('Attributes/Eyes/White_Eyes.png').convert(IMAGE_MODE), 6),
    ('Blue Eyes', Image.open('Attributes/Eyes/Blue_Eyes.png').convert(IMAGE_MODE), 6),
    ('Green Eyes', Image.open('Attributes/Eyes/Green_Eyes.png').convert(IMAGE_MODE), 6),
    ('Brown Eyes', Image.open('Attributes/Eyes/Brown_Eyes.png').convert(IMAGE_MODE), 6),
    ('Red Eyes', Image.open('Attributes/Eyes/Red_Eyes.png').convert(IMAGE_MODE), 4),
    ('Pouting Eyes', Image.open('Attributes/Eyes/Pouting_Eyes.png').convert(IMAGE_MODE), 4),
    ('Crying Black Eyes', Image.open('Attributes/Eyes/Crying_Black_Eyes.png').convert(IMAGE_MODE), 4),
    ('Bloody Black Eyes', Image.open('Attributes/Eyes/Bloody_Black_Eyes.png').convert(IMAGE_MODE), 4),
    ('Eyepatch Black Eyes', Image.open('Attributes/Eyes/Eyepatch_Black_Eyes.png').convert(IMAGE_MODE), 4),
    ('Crying Red Eyes', Image.open('Attributes/Eyes/Crying_Red_Eyes.png').convert(IMAGE_MODE), 3),
    ('Bloody Red Eyes', Image.open('Attributes/Eyes/Bloody_Red_Eyes.png').convert(IMAGE_MODE), 3),
    ('Sunglasses', Image.open('Attributes/Eyes/Sunglasses.png').convert(IMAGE_MODE), 3),
    ('VR Headset', Image.open('Attributes/Eyes/VR_Headset.png').convert(IMAGE_MODE), 3),
    ('Eyepatch Red Eyes', Image.open('Attributes/Eyes/Eyepatch_Red_Eyes.png').convert(IMAGE_MODE), 3),
    ('Glowing Green Eyes', Image.open('Attributes/Eyes/Glowing_Green_Eyes.png').convert(IMAGE_MODE), 2),
    ('Glowing Blue Eyes', Image.open('Attributes/Eyes/Glowing_Blue_Eyes.png').convert(IMAGE_MODE), 2),
    ('Glowing Red Eyes', Image.open('Attributes/Eyes/Glowing_Red_Eyes.png').convert(IMAGE_MODE), 1)
]

head_attributes = [
    # Name   # Image                            # Rarity weight
    ('NoHead', Image.new(IMAGE_MODE, IMAGE_SIZE), 10),
    ('Big Head', Image.open('Attributes/Heads/Big_Head.png').convert(IMAGE_MODE), 5),
    ('Black Buzz Cut', Image.open('Attributes/Heads/Black_Buzz_Cut.png').convert(IMAGE_MODE), 5),
    ('Red Buzz Cut', Image.open('Attributes/Heads/Red_Buzz_Cut.png').convert(IMAGE_MODE), 5),
    ('Blonde Ponytail', Image.open('Attributes/Heads/Blonde_Ponytail.png').convert(IMAGE_MODE), 5),
    ('White Ponytail', Image.open('Attributes/Heads/White_Ponytail.png').convert(IMAGE_MODE), 5),
    ('Messy Brown Hair', Image.open('Attributes/Heads/Messy_Brown_Hair.png').convert(IMAGE_MODE), 5),
    ('Messy Purple Hair', Image.open('Attributes/Heads/Messy_Purple_Hair.png').convert(IMAGE_MODE), 5),
    ('Wizard Hat', Image.open('Attributes/Heads/Wizard_Hat.png').convert(IMAGE_MODE), 4),
    ('Pirate Hat', Image.open('Attributes/Heads/Pirate_Hat.png').convert(IMAGE_MODE), 4),
    ('Bowler Hat', Image.open('Attributes/Heads/Bowler_Hat.png').convert(IMAGE_MODE), 4),
    ('Bandana', Image.open('Attributes/Heads/Bandana.png').convert(IMAGE_MODE), 4),
    ('Robin Hood Hat', Image.open('Attributes/Heads/Robin_Hood_Hat.png').convert(IMAGE_MODE), 4),
    ('Veil', Image.open('Attributes/Heads/Veil.png').convert(IMAGE_MODE), 4),
    ('Horns', Image.open('Attributes/Heads/Horns.png').convert(IMAGE_MODE), 4),
    ('Santa Hat', Image.open('Attributes/Heads/Santa_Hat.png').convert(IMAGE_MODE), 4),
    ('Mutant Head', Image.open('Attributes/Heads/Mutant_Head.png').convert(IMAGE_MODE), 3),
    ('Elf Ears', Image.open('Attributes/Heads/Elf_Ears.png').convert(IMAGE_MODE), 3),
    ('Knight Helmet', Image.open('Attributes/Heads/Knight_Helmet.png').convert(IMAGE_MODE), 3),
    ('Apple', Image.open('Attributes/Heads/Apple.png').convert(IMAGE_MODE), 3),
    ('Monobrow', Image.open('Attributes/Heads/Monobrow.png').convert(IMAGE_MODE), 3),
    ('Scar', Image.open('Attributes/Heads/Scar.png').convert(IMAGE_MODE), 2),
    ('King\'s Crown', Image.open('Attributes/Heads/King\'s_Crown.png').convert(IMAGE_MODE), 2),
    ('Queen\'s Crown', Image.open('Attributes/Heads/Queen\'s_Crown.png').convert(IMAGE_MODE), 2),
    ('Halo', Image.open('Attributes/Heads/Halo.png').convert(IMAGE_MODE), 2),
    ('Open Brain', Image.open('Attributes/Heads/Open_Brain.png').convert(IMAGE_MODE), 1),
]

base_image = Image.open('Attributes/Base.png').convert(IMAGE_MODE)

zombits = {}

features = {}

skin_weights = [skin_weight for _, _, skin_weight in skin_attributes]
eye_weights = [eye_weight for _, _, eye_weight in eye_attributes]
head_weights = [head_weight for _, _, head_weight in head_attributes]
mouth_weights = [mouth_weight for _, _, mouth_weight in mouth_attributes]
suit_weights = [suit_weight for _, _, suit_weight in suit_attributes]

alll = set()

zombit_id = 1

while len(alll) < TOTAL_ZOMBITS:
    # Pick random attributes
    while True:
        skin_name, skin_colors, _ = random.choices(population=skin_attributes, weights=skin_weights, k=1)[0]
        eye_name, eye_image, _ = random.choices(population=eye_attributes, weights=eye_weights, k=1)[0]
        head_name, head_image, _ = random.choices(population=head_attributes, weights=head_weights, k=1)[0]
        mouth_name, mouth_image, _ = random.choices(population=mouth_attributes, weights=mouth_weights, k=1)[0]
        suit_name, suit_image, _ = random.choices(population=suit_attributes, weights=suit_weights, k=1)[0]

        if not (eye_name == 'VR Headset' and mouth_name == 'Mouth') and not ((eye_name == 'Crying Red Eyes' or eye_name == 'Crying Black Eyes' or eye_name == 'Bloody Red Eyes' or eye_name == 'Bloody Black Eyes') and (mouth_name == 'Creeper Mouth' or mouth_name == 'Big Lips' or mouth_name == 'Tusks')):
            break

    primary_skin_color, secondary_skin_color, tertiary_skin_color, outline_color = skin_colors
    
    # Replace base skin color
    base_image_data = np.array(base_image)
    red, green, blue = base_image_data[:,:,0], base_image_data[:,:,1], base_image_data[:,:,2]

    primary_color_mask = (red == 204) & (green == 204) & (blue == 119)
    secondary_color_mask = (red == 170) & (green == 170) & (blue == 85)
    tertiary_color_mask = (red == 136) & (green == 136) & (blue == 68)
    outline_color_mask = (red == 34) & (green == 32) & (blue == 52)

    base_image_data[:,:,:3][primary_color_mask] = primary_skin_color
    base_image_data[:,:,:3][secondary_color_mask] = secondary_skin_color
    base_image_data[:,:,:3][tertiary_color_mask] = tertiary_skin_color
    base_image_data[:,:,:3][outline_color_mask] = outline_color
    base_image_new = Image.fromarray(base_image_data)

    # Replace base skin color
    mouth_image_data = np.array(mouth_image)
    red, green, blue = mouth_image_data[:,:,0], mouth_image_data[:,:,1], mouth_image_data[:,:,2]

    primary_color_mask = (red == 204) & (green == 204) & (blue == 119)
    secondary_color_mask = (red == 170) & (green == 170) & (blue == 85)
    tertiary_color_mask = (red == 136) & (green == 136) & (blue == 68)
    outline_color_mask = (red == 34) & (green == 32) & (blue == 52)

    mouth_image_data[:,:,:3][primary_color_mask] = primary_skin_color
    mouth_image_data[:,:,:3][secondary_color_mask] = secondary_skin_color
    mouth_image_data[:,:,:3][tertiary_color_mask] = tertiary_skin_color
    mouth_image_data[:,:,:3][outline_color_mask] = outline_color
    mouth_image_new = Image.fromarray(mouth_image_data)

    # Replace base skin color
    head_image_data = np.array(head_image)
    red, green, blue = head_image_data[:,:,0], head_image_data[:,:,1], head_image_data[:,:,2]

    primary_color_mask = (red == 204) & (green == 204) & (blue == 119)
    secondary_color_mask = (red == 170) & (green == 170) & (blue == 85)
    tertiary_color_mask = (red == 136) & (green == 136) & (blue == 68)
    outline_color_mask = (red == 34) & (green == 32) & (blue == 52)

    head_image_data[:,:,:3][primary_color_mask] = primary_skin_color
    head_image_data[:,:,:3][secondary_color_mask] = secondary_skin_color
    head_image_data[:,:,:3][tertiary_color_mask] = tertiary_skin_color
    head_image_data[:,:,:3][outline_color_mask] = outline_color
    head_image_new = Image.fromarray(head_image_data)

    if (((eye_name == 'Pouting Eyes') and (head_name == 'Knight Helmet')) or
        ((eye_name == 'Eyepatch Black Eyes' or eye_name == 'Eyepatch Red Eyes') and (head_name == 'Pirate Hat'))):
        final_image = Image.alpha_composite(Image.alpha_composite(Image.alpha_composite(Image.alpha_composite(base_image_new, suit_image), eye_image), mouth_image_new), head_image_new)
    elif (((eye_name == 'Crying Red Eyes' or eye_name == 'Crying Black Eyes' or eye_name == 'Bloody Red Eyes' or eye_name == 'Bloody Black Eyes') and (mouth_name == 'Blunt' or mouth_name == 'Snout')) or
        ((eye_name == 'Eyepatch Black Eyes' or eye_name == 'Eyepatch Red Eyes' or eye_name == 'Pouting Eyes') and (mouth_name == 'Snout' or mouth_name == 'Big Lips' or mouth_name == 'Tusks')) or
        ((eye_name == 'Sunglasses') and (mouth_name == 'Snout')) or
        ((head_name == 'Veil') and (mouth_name == 'Blunt' or mouth_name == 'Big Lips' or mouth_name == 'Snout'))):
        
        final_image = Image.alpha_composite(Image.alpha_composite(Image.alpha_composite(Image.alpha_composite(base_image_new, suit_image), head_image_new), eye_image), mouth_image_new)
        # Extend eyepatch
        if eye_name == 'Eyepatch Black Eyes' or eye_name == 'Eyepatch Red Eyes':
            final_image_data = np.array(final_image)
            if not ((final_image_data[9,12,0] == outline_color[0] and final_image_data[9,12,1] == outline_color[1] and final_image_data[9,12,2] == outline_color[2]) or (final_image_data[9,14,0] == outline_color[0] and final_image_data[9,14,1] == outline_color[1] and final_image_data[9,14,2] == outline_color[2])):
                current_y = 8
                while not (final_image_data[current_y,13,0] == outline_color[0] and final_image_data[current_y,13,1] == outline_color[1] and final_image_data[current_y,13,2] == outline_color[2]):
                    final_image_data[current_y,13,:] = [34, 32, 52, 255]
                    current_y -= 1
                final_image = Image.fromarray(final_image_data)
    else:
        final_image = Image.alpha_composite(Image.alpha_composite(Image.alpha_composite(Image.alpha_composite(base_image_new, suit_image), mouth_image_new), head_image_new), eye_image)
        # Extend eyepatch
        if eye_name == 'Eyepatch Black Eyes' or eye_name == 'Eyepatch Red Eyes':
            final_image_data = np.array(final_image)
            if not ((final_image_data[9,12,0] == outline_color[0] and final_image_data[9,12,1] == outline_color[1] and final_image_data[9,12,2] == outline_color[2]) or (final_image_data[9,14,0] == outline_color[0] and final_image_data[9,14,1] == outline_color[1] and final_image_data[9,14,2] == outline_color[2])):
                current_y = 8
                while not (final_image_data[current_y,13,0] == outline_color[0] and final_image_data[current_y,13,1] == outline_color[1] and final_image_data[current_y,13,2] == outline_color[2]):
                    final_image_data[current_y,13,:] = [34, 32, 52, 255]
                    current_y -= 1
                final_image = Image.fromarray(final_image_data) 

    if ((head_name == 'Knight Helmet')):
        print("KNIGHT HELMET:", zombit_id)
    if ((head_name == 'Pirate Hat')):
        print("PIRATE HAT:", zombit_id)
    if ((head_name == 'Knight Helmet') and (eye_name == 'Pouting Eyes')):
        print(f"POUTING & KNIGHT HELMET: {zombit_id}")

    if ((skin_name == 'Void') and (head_name == 'Knight Helmet') and (eye_name == 'Pouting Eyes')):
        print(f"VOID & POUTING & KNIGHT HELMET: {zombit_id}")

    if tuple(np.array(final_image).flatten()) in alll:
        continue
    alll.add(tuple(np.array(final_image).flatten()))

    # Create final image
    final_image.save(f'Final/Zombit{zombit_id}.png')

    attrs = [skin_name, eye_name]
    if head_name != 'NoHead':
        attrs.append(head_name)
    if suit_name != 'NoSuit':
        attrs.append(suit_name)
    if mouth_name != 'NoMouth':
        attrs.append(mouth_name)
    zombits[zombit_id] = attrs
    
    if eye_name in features:
        features[eye_name].append(zombit_id)
    else:
        features[eye_name] = [zombit_id]

    if head_name in features:
        features[head_name].append(zombit_id)
    elif head_name != 'NoHead':
        features[head_name] = [zombit_id]

    if mouth_name in features:
        features[mouth_name].append(zombit_id)
    elif mouth_name != 'NoMouth':
        features[mouth_name] = [zombit_id]

    if suit_name in features:
        features[suit_name].append(zombit_id)
    elif suit_name != 'NoSuit':
        features[suit_name] = [zombit_id]

    if skin_name in features:
        features[skin_name].append(zombit_id)
    else:
        features[skin_name] = [zombit_id]

    zombit_id += 1

features_count = {}

zombits2 = {}

for feature in features:
    amount_with_feature = len(features[feature])
    rarity = amount_with_feature/TOTAL_ZOMBITS * 100
    for zombit_number in features[feature]:
        if zombit_number in zombits2:
            zombits2[zombit_number].append((feature, amount_with_feature, rarity))
        else:
            zombits2[zombit_number] = [(feature, amount_with_feature, rarity)]

for feature in features:
    amount_with_feature = len(features[feature])
    rarity = amount_with_feature/TOTAL_ZOMBITS * 100
    features_count[feature] = (amount_with_feature, rarity)

zombits2_file = open("zombits_rarity.json", "w")
json.dump(zombits2, zombits2_file, sort_keys=True, indent=2)
zombits2_file.close()

zombits_file = open("zombits.json", "w")
json.dump(zombits, zombits_file, indent=2)
zombits_file.close()

features_file = open("features.json", "w")
json.dump(features, features_file, indent=2)
features_file.close()

features_count_file = open("features_count.json", "w")
json.dump(features_count, features_count_file, indent=2)
features_count_file.close()
