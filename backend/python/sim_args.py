import argparse


from backend.python.enums import Containment


def get_args(name):
    parser = argparse.ArgumentParser(description='Create emulator for COVID-19 pandemic')
    parser.add_argument('--name', help="Name of the simulation", default=name)
    parser.add_argument('--inf_initial', help='initial infected %', type=int, default=0.01)
    parser.add_argument('--sim_days', help='Number of simulation days', type=int, default=60)

    parser.add_argument('--inf_radius', help='infection radius', type=float, default=1)
    parser.add_argument('--common_fever_p', help='common fever probability', type=float, default=0.1)

    # parser.add_argument('--containment_strategy', help='containment strategy used', type=str, default=Containment.NONE.name)
    # parser.add_argument('--roster_groups', help='Number of groups ', type=int, default=2, choices=range(1, 6))

    parser.add_argument('--testing_strategy', help='testing strategy used (0-NONE, 1-HOSPITAL)', default="HOSPITAL")
    parser.add_argument('--n_test_centers', help='Number of test centers', type=int, default=3)
    parser.add_argument('--r_test_centers', help='Mean radius of coverage from the test center', type=int, default=20)

    parser.add_argument('--load_log_name', help='Log root location to load', type=str, default=None)
    parser.add_argument('--load_log_day', help='Log day to load', type=int, default=-1)

    parser.add_argument('--social_distance', help='Override social distancing of all locations', type=str, default="-1")
    parser.add_argument('--hygiene_p', help='Override unhygienic probability of all people', type=str, default="-1")
    parser.add_argument('--base_transmission_p', help='Base transmission probability of the disease variant', type=str, default="0.01")
    parser.add_argument('--incubation_days', help='Incubation period in days', type=str, default="3")
    return parser


def get_args_web_ui(name):
    parser = argparse.ArgumentParser(description='Create emulator for COVID-19 pandemic')
    parser.add_argument('--name', help="Name of the simulation", default=name)
    # parser.add_argument('--inf_initial', help='initial infected %', type=float, default=0.01)
    parser.add_argument('--sim_days', help='Number of simulation days', type=int, default=60)

    parser.add_argument('--inf_radius', help='infection radius', type=float, default=1)
    parser.add_argument('--common_fever_p', help='common fever probability', type=float, default=0.1)

    # parser.add_argument('--containment_strategy', help='containment strategy used', default=Containment.NONE.name)
    # parser.add_argument('--roster_groups', help='Number of groups ', type=int, default=2, choices=range(1, 6))

    parser.add_argument('--testing_strategy', help='testing strategy used (0-NONE, 1-HOSPITAL)', default="HOSPITAL")
    parser.add_argument('--n_test_centers', help='Number of test centers', type=int, default=3)
    parser.add_argument('--r_test_centers', help='Mean radius of coverage from the test center', type=int, default=20)

    parser.add_argument('--load_log_name', help='Log root location to load', type=str, default=None)
    parser.add_argument('--load_log_day', help='Log day to load', type=str, default=-1)

    parser.add_argument('--locationTreeData', help='File name of location tree data which stores JSON string', type=str)
    parser.add_argument('--personPercentData', help='Percentage of each population class', type=str)
    parser.add_argument('--addedContainmentEvents', help='Containment events', type=str)
    parser.add_argument('--addedGatheringEvents', help='Gathering events', type=str)
    parser.add_argument('--addedVaccinationEvents', help='Vaccination events', type=str)

    parser.add_argument('--social_distance', help='Override social distancing of all locations', type=str, default="-1")
    parser.add_argument('--hygiene_p', help='Override unhygienic probability of all people', type=str, default="-1")
    parser.add_argument('--base_transmission_p', help='Base transmission probability of the disease variant', type=str,
                        default="0.01")
    parser.add_argument('--incubation_days', help='Incubation period in days', type=str, default="3")
    return parser
