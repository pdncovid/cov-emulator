from backend.python.Time import Time
from backend.python.functions import bs
from backend.python.location.Blocks.RuralBlock import RuralBlock
from backend.python.location.Blocks.UrbanBlock import UrbanBlock
from backend.python.location.Cemetery import Cemetery
from backend.python.location.Commercial.CommercialBuilding import CommercialBuilding
from backend.python.location.Commercial.CommercialCanteen import CommercialCanteen
from backend.python.location.Commercial.CommercialWorkArea import CommercialWorkArea
from backend.python.location.Commercial.CommercialZone import CommercialZone
from backend.python.location.Districts.DenseDistrict import DenseDistrict
from backend.python.location.Education.Classroom import Classroom
from backend.python.location.Education.EducationZone import EducationZone
from backend.python.location.Education.School import School
from backend.python.location.Education.SchoolCanteen import SchoolCanteen
from backend.python.location.Industrial.GarmentBuilding import GarmentBuilding
from backend.python.location.Industrial.GarmentCanteen import GarmentCanteen
from backend.python.location.Industrial.GarmentOffice import GarmentOffice
from backend.python.location.Industrial.GarmentWorkArea import GarmentWorkArea
from backend.python.location.Industrial.IndustrialZone import IndustrialZone
from backend.python.location.Location import Location
from backend.python.location.Medical.COVIDQuarantineZone import COVIDQuarantineZone
from backend.python.location.Medical.Hospital import Hospital
from backend.python.location.Medical.MedicalZone import MedicalZone
from backend.python.location.Residential.Home import Home
from backend.python.location.Residential.ResidentialPark import ResidentialPark
from backend.python.location.Residential.ResidentialZone import ResidentialZone
from backend.python.location.TestCenter import TestCenter
from backend.python.point.BusDriver import BusDriver
from backend.python.point.CommercialWorker import CommercialWorker
from backend.python.point.CommercialZoneBusDriver import CommercialZoneBusDriver
from backend.python.point.GarmentAdmin import GarmentAdmin
from backend.python.point.GarmentWorker import GarmentWorker
from backend.python.point.SchoolBusDriver import SchoolBusDriver
from backend.python.point.Student import Student
from backend.python.point.TuktukDriver import TuktukDriver

default_infectiousness = {
    DenseDistrict: 0.8,

    UrbanBlock: 0.8,
    RuralBlock: 0.6,

    CommercialBuilding: 0.8,
    CommercialCanteen: 0.9,
    CommercialWorkArea: 0.99,
    CommercialZone: 0.7,

    GarmentBuilding: 0.8,
    GarmentCanteen: 0.9,
    GarmentWorkArea: 0.99,
    GarmentOffice: 0.9,
    IndustrialZone: 0.7,

    Classroom: 0.9,
    School: 0.8,
    SchoolCanteen: 0.99,
    EducationZone: 0.7,

    Hospital: 0.8,
    COVIDQuarantineZone: 1.0,
    MedicalZone: 0.85,

    Home: 0.8,
    ResidentialPark: 0.7,
    ResidentialZone: 0.7,

    Cemetery: 0.0,
    TestCenter: 0.9,
}
work_map = {
    CommercialWorker: CommercialZone,
    GarmentWorker: IndustrialZone,
    GarmentAdmin: IndustrialZone,
    Student: EducationZone,
    BusDriver: None,
    TuktukDriver: None,
    CommercialZoneBusDriver: CommercialBuilding,
    SchoolBusDriver: School
}

loc_at_t = {
    CommercialWorker: {
        Time.get_time_from_dattime(7, 0): 'home',
        Time.get_time_from_dattime(17, 0): 'work',

    },
    GarmentWorker: {
        Time.get_time_from_dattime(7, 0): 'home',
        Time.get_time_from_dattime(17, 0): 'work',

    },
    GarmentAdmin: {
        Time.get_time_from_dattime(9, 0): 'home',
        Time.get_time_from_dattime(17, 0): 'work',

    },
    Student: {
        Time.get_time_from_dattime(7, 0): 'home',
        Time.get_time_from_dattime(14, 0): 'work',

    },
    BusDriver: {
        Time.get_time_from_dattime(5, 0): 'home',
        Time.get_time_from_dattime(6, 0): ResidentialZone,
        Time.get_time_from_dattime(7, 0): CommercialZone,
        Time.get_time_from_dattime(8, 0): EducationZone,
        Time.get_time_from_dattime(9, 0): IndustrialZone,
        Time.get_time_from_dattime(10, 0): CommercialZone,

        Time.get_time_from_dattime(13, 0): IndustrialZone,
        Time.get_time_from_dattime(14, 0): EducationZone,
        Time.get_time_from_dattime(15, 0): IndustrialZone,
        Time.get_time_from_dattime(16, 0): CommercialZone,
    },
    TuktukDriver: {
        Time.get_time_from_dattime(5, 0): 'home',
        Time.get_time_from_dattime(6, 0): ResidentialZone,
        Time.get_time_from_dattime(7, 0): CommercialZone,
        Time.get_time_from_dattime(8, 0): EducationZone,
        Time.get_time_from_dattime(9, 0): IndustrialZone,
        Time.get_time_from_dattime(10, 0): CommercialZone,

        Time.get_time_from_dattime(13, 0): IndustrialZone,
        Time.get_time_from_dattime(14, 0): EducationZone,
        Time.get_time_from_dattime(15, 0): IndustrialZone,
        Time.get_time_from_dattime(16, 0): CommercialZone,
    },
    CommercialZoneBusDriver: {
        Time.get_time_from_dattime(5, 0): 'home',
        Time.get_time_from_dattime(6, 0): ResidentialZone,
        Time.get_time_from_dattime(6, 30): ResidentialZone,
        Time.get_time_from_dattime(7, 0): CommercialZone,

        Time.get_time_from_dattime(17, 0): CommercialZone,
        Time.get_time_from_dattime(17, 15): ResidentialZone,
        Time.get_time_from_dattime(17, 30): ResidentialZone,

    },
    SchoolBusDriver: {
        Time.get_time_from_dattime(5, 0): 'home',
        Time.get_time_from_dattime(6, 0): ResidentialZone,
        Time.get_time_from_dattime(6, 30): ResidentialZone,
        Time.get_time_from_dattime(7, 0): EducationZone,

        Time.get_time_from_dattime(14, 0): EducationZone,
        Time.get_time_from_dattime(14, 15): ResidentialZone,
        Time.get_time_from_dattime(14, 30): ResidentialZone,
    },

}


def get_loc_for_p_at_t(p, t):
    timeline = loc_at_t[p.__class__]
    keys = list(timeline.keys())
    idx = bs(keys, t)
    if idx == len(timeline.keys()):
        return []
    suggestion = timeline[keys[idx]]
    if suggestion == 'home':
        return [p.home_loc]
    if suggestion == 'work':
        return [p.work_loc]
    if type(suggestion) == str:
        raise Exception()
    return [suggestion]


def get_dur_for_p_in_loc_at_t(p, loc, t):
    return Time.get_duration(0.5)


if __name__ == "__main__":
    p = CommercialWorker()
    print(get_loc_for_p_at_t(p, Time.get_time_from_dattime(6, 59)))
    print(get_loc_for_p_at_t(p, Time.get_time_from_dattime(7, 0)))
    print(get_loc_for_p_at_t(p, Time.get_time_from_dattime(7, 1)))
