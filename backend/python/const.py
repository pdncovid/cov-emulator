from backend.python.location.Blocks.RuralBlock import RuralBlock
from backend.python.location.Blocks.UrbanBlock import UrbanBlock
from backend.python.location.Cemetery import Cemetery
from backend.python.location.Commercial.CommercialBuilding import CommercialBuilding
from backend.python.location.Commercial.CommercialCanteen import CommercialCanteen
from backend.python.location.Commercial.CommercialWorkArea import CommercialWorkArea
from backend.python.location.Commercial.CommercialZone import CommercialZone
from backend.python.location.Districts.DenseDistrict import DenseDistrict
from backend.python.location.Districts.SparseDistrict import SparseDistrict
from backend.python.location.Education.Classroom import Classroom
from backend.python.location.Education.EducationZone import EducationZone
from backend.python.location.Education.School import School
from backend.python.location.Education.SchoolCanteen import SchoolCanteen
from backend.python.location.GatheringPlace import GatheringPlace
from backend.python.location.Industrial.GarmentBuilding import GarmentBuilding
from backend.python.location.Industrial.GarmentCanteen import GarmentCanteen
from backend.python.location.Industrial.GarmentOffice import GarmentOffice
from backend.python.location.Industrial.GarmentWorkArea import GarmentWorkArea
from backend.python.location.Industrial.IndustrialZone import IndustrialZone
from backend.python.location.Medical.COVIDQuarantineZone import COVIDQuarantineZone
from backend.python.location.Medical.Hospital import Hospital
from backend.python.location.Medical.MedicalZone import MedicalZone
from backend.python.location.Residential.Home import Home
from backend.python.location.Residential.ResidentialPark import ResidentialPark
from backend.python.location.Residential.ResidentialZone import ResidentialZone
from backend.python.location.Stations.BusStation import BusStation
from backend.python.location.Stations.TukTukStation import TukTukStation
from backend.python.location.TestCenter import TestCenter
from backend.python.point.BusDriver import BusDriver
from backend.python.point.CommercialWorker import CommercialWorker
from backend.python.point.GarmentAdmin import GarmentAdmin
from backend.python.point.GarmentWorker import GarmentWorker
from backend.python.point.Infant import Infant
from backend.python.point.Retired import Retired
from backend.python.point.Student import Student
from backend.python.point.Teacher import Teacher
from backend.python.point.TuktukDriver import TuktukDriver
from backend.python.location.Province.AvgProvince import AvgProvince

default_infectiousness = {
    AvgProvince: 0.7,

    DenseDistrict: 0.8,
    SparseDistrict: 0.8,

    UrbanBlock: 0.8,
    RuralBlock: 0.6,

    BusStation: 0.9,
    TukTukStation: 0.8,

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

    GatheringPlace: 0.9,
    Cemetery: 0.0,
    TestCenter: 0.9,
}

default_happiness_boost = {
    AvgProvince: 0.0,

    DenseDistrict: 0.0,
    SparseDistrict: 0.0,

    UrbanBlock: 0.8,
    RuralBlock: 0.5,

    BusStation: -0.1,
    TukTukStation: -0.1,

    CommercialBuilding: -0.3,
    CommercialCanteen: 0.9,
    CommercialWorkArea: -0.2,
    CommercialZone: -0.3,

    GarmentBuilding: -0.5,
    GarmentCanteen: 0.9,
    GarmentWorkArea: -0.3,
    GarmentOffice: -0.5,
    IndustrialZone: -0.3,

    Classroom: -0.2,
    School: 0.1,
    SchoolCanteen: 0.99,
    EducationZone: 0.1,

    Hospital: -0.8,
    COVIDQuarantineZone: -1.0,
    MedicalZone: -0.85,

    Home: 0.0,
    ResidentialPark: 0.7,
    ResidentialZone: 0.7,

    GatheringPlace: 0.9,
    Cemetery: 0.0,
    TestCenter: -0.9,
}

work_map = {
    CommercialWorker: 'CommercialWorkArea',
    GarmentWorker: 'GarmentWorkArea',
    GarmentAdmin: 'GarmentOffice',
    Student: 'Classroom',
    Teacher: 'Classroom',
    BusDriver: 'BusStation',
    TuktukDriver: 'TukTukStation',
    Retired: None,
    Infant: None,
}
