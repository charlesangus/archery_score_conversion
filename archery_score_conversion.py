import random
import pprint
import math
import argparse


BASE_TARGET_DIAMETER = 122
# BASE_RANGE = 7000
# PERFECT_SCORE = 720


def two_d_random(mu, sigma):
    rand_func = random.gauss
    return pow((pow(rand_func(mu, sigma), 2) + pow(rand_func(mu, sigma), 2)), .5)


rand_func = two_d_random

def shoot_arrows(num_shots, sd, gnas=False):
    offsets = [abs(rand_func(0, sd)) for i in range(num_shots)]
    score = 0
    target_size = BASE_TARGET_DIAMETER / 2.0
    if not gnas:
        score_widths = [BASE_TARGET_DIAMETER / 2.0,
                (BASE_TARGET_DIAMETER * .9) / 2.0,
                (BASE_TARGET_DIAMETER * .8) / 2.0,
                (BASE_TARGET_DIAMETER * .7)/ 2.0,
                (BASE_TARGET_DIAMETER * .6) / 2.0,
                (BASE_TARGET_DIAMETER * .5) / 2.0,
                (BASE_TARGET_DIAMETER * .4) / 2.0,
                (BASE_TARGET_DIAMETER * .3) / 2.0,
                (BASE_TARGET_DIAMETER * .2) / 2.0,
                (BASE_TARGET_DIAMETER * .1) / 2.0,
                ]
            
        for offset in offsets:
            for score_width in score_widths:
                if offset < score_width:
                    score = score + 1
    else:
        score_widths = [BASE_TARGET_DIAMETER / 2.0,
                (BASE_TARGET_DIAMETER * .8) / 2.0,
                (BASE_TARGET_DIAMETER * .6) / 2.0,
                (BASE_TARGET_DIAMETER * .4) / 2.0,
                (BASE_TARGET_DIAMETER * .2) / 2.0,
                ]
        
        # should be 1, 3, 5, 7, 9
        
        for offset in offsets:
            if offset < score_widths[0]:
                score = score + 1
            if offset < score_widths[1]:
                score = score + 2
            if offset < score_widths[2]:
                score = score + 2
            if offset < score_widths[3]:
                score = score + 2
            if offset < score_widths[4]:
                score = score + 2
                
        #for offset in offsets:
            #for score_width in score_widths:
                #if offset < score_width:
                    #score = score + 2
    
    return score

def find_best_fit_sd(target_score,
                     tolerance,
                     GNAS,
                     BASE_ARROWS,
                     ):

    min_sd = 0
    max_sd = BASE_TARGET_DIAMETER * 2
    last_sd = 0
    sd = BASE_TARGET_DIAMETER
    
    last_score = 0
    score = shoot_arrows(BASE_ARROWS, sd, gnas=GNAS)
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
        score = shoot_arrows(BASE_ARROWS, sd, gnas=GNAS)
        difference = abs(target_score - score)
    
    return sd

def find_average_best_fit_sd(target_score,
                             tolerance,
                             trials,
                             GNAS,
                             BASE_ARROWS,
                             ):

    sds = [find_best_fit_sd(target_score, tolerance, GNAS, BASE_ARROWS,) for i in range(trials)]
    average_sd = sum(sds)/float(len(sds))

    return average_sd


def find_new_hit_rate(target_score,
                      tolerance,
                      trials,
                      num_shots,
                      theta_of_desired_target,
                      GNAS,
                      BASE_ARROWS,
                      BASE_RANGE,
                      desired_range,
                      desired_target_radius,
                      ):


    final_sd = find_average_best_fit_sd(target_score,
                                        tolerance,
                                        trials,
                                        GNAS,
                                        BASE_ARROWS,
                                        )

    theta_of_final_sd = math.atan(final_sd / BASE_RANGE)

    radian_offsets = [abs(rand_func(0, theta_of_final_sd)) for i in range(num_shots)]
    hits = [shot for shot in radian_offsets if shot < theta_of_desired_target]
    hit_rate = len(hits) / float(len(radian_offsets))
    
    
    # trying different way of calculatiing hit rate
    final_sd_at_target_range = final_sd / (desired_range / BASE_RANGE)
    offsets = [abs(rand_func(0, final_sd_at_target_range)) for i in range(num_shots)]
    hits = [shot for shot in offsets if shot < desired_target_radius]
    hit_rate = len(hits) / float(len(radian_offsets))
    
    return hit_rate

def main():
        
    parser = argparse.ArgumentParser(description='Take a score out of 720 from an archery competition (122cm target at 70m, 72 shots, scores from 0-10 per shot) and convert it to a hit rate for a given target range and target size.')
    parser.add_argument('score', metavar='720 score', type=int, help="Score to use as a definition of our putative archer's abilit.")
    parser.add_argument('desired_range', metavar='target range', type=int, help='How far the output target is from the shooter, in meters.')
    parser.add_argument('desired_target_diameter', metavar='target diameter', type=int, help='Diameter of the desired target in cm. Targets are always circular.')
    parser.add_argument('--tolerance', type=int, help='Tolerance when searching for the best fit standard deviation for the given score. Larger numbers are faster but less accurate.', default=3)
    parser.add_argument('--trials', type=int, help='How many times to run the best fit standard deviation search for the given score. LArger numbers are slower but more accurate.', default=100)
    parser.add_argument('--num_shots', type=int, help='How many shots to take at the new range and target size to determine the hit rate. Larger numbers are slower but more accurate', default=10000)
    parser.add_argument('--gnas', action='store_true', help="If the round you're using as input uses GNAS 5-zone scoring on a 122cm boss, set this flag.")
    parser.add_argument('--base_arrows', type=int, default=72, help="If the round you're using as input uses a different number of arrows than 72, enter that number here.")
    parser.add_argument('--base_range', type=int, default=70, help="If the round you're using as input uses a different range than 70m, enter that range here (in meters).")
    args = parser.parse_args()

    target_score = args.score
    desired_target_radius = args.desired_target_diameter / 2.0
    desired_range = args.desired_range * 100
    theta_of_desired_target = math.atan(desired_target_radius / float(desired_range))
    tolerance = args.tolerance
    trials = args.trials
    num_shots = args.num_shots
    
    GNAS = args.gnas
    BASE_ARROWS = args.base_arrows
    BASE_RANGE = args.base_range * 100

    hit_rate = find_new_hit_rate(target_score,
                                 tolerance,
                                 trials,
                                 num_shots,
                                 theta_of_desired_target,
                                 GNAS,
                                 BASE_ARROWS,
                                 BASE_RANGE,
                                 desired_range,
                                 desired_target_radius,
                                 )
    hit_rate_twenty = round(hit_rate * 20)
    print('Input: {target_score} at range {BASE_RANGE}m and target diameter {BASE_TARGET_DIAMETER}cm'.format(target_score=target_score, BASE_RANGE=BASE_RANGE / 100, BASE_TARGET_DIAMETER=BASE_TARGET_DIAMETER))
    print('Converted to: range {desired_range}m and target diameter {desired_target_diameter}cm'.format(desired_range=args.desired_range, desired_target_diameter=args.desired_target_diameter))
    print('Hit rate: %s' % hit_rate)
    print('Hit rate %s/20' % hit_rate_twenty)

if __name__ == "__main__":
    main()

