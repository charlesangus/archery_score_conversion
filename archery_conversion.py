import random
import pprint
import math
import argparse

parser = argparse.ArgumentParser(description='Take a score out of 720 from an archery competition (122cm target at 70m, 72 shots, scores from 0-10 per shot) and convert it to a hit rate for a given target range and target size.')
parser.add_argument('score', metavar='720 score', type=int, help="Score to use as a definition of our putative archer's abilit.")
parser.add_argument('desired_range', metavar='target range', type=int, help='How far the output target is from the shooter, in meters.')
parser.add_argument('desired_target_diameter', metavar='target diameter', type=int, help='Diameter of the desired target in cm. Targets are always circular.')
args = parser.parse_args()

# all units in cm

def shoot_arrows(num_shots, sd, print_all_shots=False):

    offsets = []
    score = 0
    target_size = 122/2.0
    hit_rate_target_size = 122/2.0
    score_widths = [122/2.0,
              109.8/2.0,
              97.6/2.0,
              85.4/2.0,
              73.2/2.0,
              61.0/2.0,
              48.4/2.0,
              36.6/2.0,
              24.4/2.0,
              12.2/2.0,
              ]

    for i in range(num_shots):
        offsets.append(abs(random.gauss(0, sd)))
        
    for offset in offsets:
        for score_width in score_widths:
            if offset < score_width:
                score = score + 1

    if print_all_shots:
        pprint.pprint(sorted(offsets))
        hits = [offset for offset in offsets if offset < hit_rate_target_size]
        hit_rate = len(hits)/float(len(offsets))
        print("Hit target: %s" % hit_rate)
        print("Hit target %s/20" % round(hit_rate*20.0))
    return score

target_score = args.score
tolerance = 3
trials = 100
sds = []

for i in range(trials):
    last_sd = 0
    sd = 122
    difference = 1000
    last_score = 0
    max_sd = 122
    min_sd = 0
    score = shoot_arrows(72, sd)
    difference = abs(target_score - score)
    
    while difference > tolerance:
        if score > target_score and last_score > target_score:
            # then SD is too small, must increase
            # we haven't bracketed, so just go halfway to a reasonable maximum
            new_sd = (sd + max_sd) / 2.0
            min_sd = sd
            last_sd = sd
            sd = new_sd
        elif score > target_score and last_score < target_score:
            # then SD is too small, must increase
            # but the truth is between this sd and the last sd
            new_sd = (sd + last_sd) / 2.0
            min_sd = sd
            last_sd = sd
            sd = new_sd
        elif score < target_score and last_score < target_score:
            # then SD is too big, must decrease
            # we haven't bracketed, so just make it half as big
            new_sd = (sd + min_sd) / 2.0
            max_sd = sd
            last_sd = sd
            sd = new_sd
        elif score < target_score and last_score > target_score:
            # then SD is too big, must decrease
            # but the truth is between this and the last sd
            new_sd = (sd + last_sd) / 2.0
            max_sd = sd
            last_sd = sd
            sd = new_sd
        last_score = score
        score = shoot_arrows(72, sd)
        difference = abs(target_score - score)
        # print("Score: %s" % score)
        # print("Dif  : %s" % difference)
        # print("SD   : %s" % sd)
    sds.append(sd)

final_sd = sum(sds)/float(len(sds))
theta_of_final_sd = math.atan(final_sd/7000)

desired_target_radius = args.desired_target_diameter / 2.0
desired_range = args.desired_range * 100
theta_of_desired_target = math.atan(desired_target_radius / float(desired_range))

num_shots = 1000
radian_offsets = []
for i in range(num_shots):
    radian_offset = abs(random.gauss(0, theta_of_final_sd))
    # print(radian_offset)
    radian_offsets.append(radian_offset)
hits = [shot for shot in radian_offsets if shot < theta_of_desired_target]
hit_rate = len(hits) / float(len(radian_offsets))
hit_rate_twenty = round(hit_rate * 20)

print('Hit rate: %s' % hit_rate)
print('Hit rate %s/20' % hit_rate_twenty)

