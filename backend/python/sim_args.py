import argparse


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

    parser.add_argument('--load_log_name', help='Log root location to load', type=str, default='NONE')
    parser.add_argument('--load_log_day', help='Log day to load', type=str, default=-1)

    parser.add_argument('--locationTreeData', help='File name of location tree data which stores JSON string', type=str, default="temp.tree")
    parser.add_argument('--personPercentData', help='Percentage of each population class', type=str,
                        default="""{"0":{"p_class":"BusDriver","percentage":"10","ipercentage":"0"},"1":{"p_class":"CommercialWorker","percentage":"15","ipercentage":5},"2":{"p_class":"GarmentAdmin","percentage":"2","ipercentage":5},"3":{"p_class":"GarmentWorker","percentage":"10","ipercentage":5},"4":{"p_class":"Infant","percentage":"5","ipercentage":"0"},"5":{"p_class":"Retired","percentage":"5","ipercentage":"0"},"6":{"p_class":"Student","percentage":"12","ipercentage":"0"},"7":{"p_class":"Teacher","percentage":"3","ipercentage":"0"},"8":{"p_class":"TuktukDriver","percentage":"5","ipercentage":"0"},"9":{"p_class":"MedicalWorker","percentage":"10","ipercentage":"0"},"10":{"p_class":"RetailShopWorker","percentage":"3","ipercentage":"0"},"11":{"p_class":"BankWorker","percentage":"4","ipercentage":"0"},"12":{"p_class":"AdministrativeWorkers","percentage":"2","ipercentage":"0"},"13":{"p_class":"EstateWorkers","percentage":"5","ipercentage":"0"},"14":{"p_class":"PlantCultivators","percentage":"2","ipercentage":"0"},"15":{"p_class":"LivestockCultivators","percentage":"2","ipercentage":"0"}}""")
    parser.add_argument('--addedContainmentEvents', help='Containment events', type=str, default="""{"0":{"id":0,"startday":"0","containment_strategy":"NONE","roster_groups":"1"}}""")
    parser.add_argument('--addedGatheringEvents', help='Gathering events', type=str, default="{}")
    parser.add_argument('--addedVaccinationEvents', help='Vaccination events', type=str, default="{}")
    parser.add_argument('--addedVariantEvents', help='Variant events', type=str, default="""{"0":{"id":0,"name":"Base","day":"0","transmittable":"0.5","severity":"0.5"},"1":{"id":1,"name":"Delta","day":"1","transmittable":"0.4","severity":"0.7"}}""")

    parser.add_argument('--social_distance', help='Override social distancing of all locations', type=str, default="0.1")
    parser.add_argument('--hygiene_p', help='Override unhygienic probability of all people', type=str, default="-1")
    parser.add_argument('--base_transmission_p', help='Base transmission probability of the disease variant', type=str,
                        default="0.01")
    parser.add_argument('--incubation_days', help='Incubation period in days', type=str, default="1")
    parser.add_argument('--log_fine_details', help='Log position, contacts etc. (0-no, 1-yes)', type=int, default=1)
    parser.add_argument('--analyze_infect_contacts_only', help='Store contact info of infected people only', type=int, default=1)

    return parser
