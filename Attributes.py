from pprint import pprint

class Attributes:
    talker = "talker"

    # GGA
    timestamp = "timestamp"
    lat = "lat"
    lat_dir = "lat_dir"
    lon = "lon"
    lon_dir = "lon_dir"
    gps_qual = "gps_qual"
    num_sats = "num_sats"
    hdop = "hdop"
    altitude = "altitude"
    altitude_units = "altitude_units"
    geo_sep = "geo_sep"
    geo_sep_units = "geo_sep_units"
    gps_diff_age = "gps_diff_age"
    ref_station_id = "ref_station_id"

    # GSA
    mode = "mode"
    mode_fix = "mode_fix"
    sv_id01 = "sv_id01"
    sv_id02 = "sv_id02"
    sv_id03 = "sv_id03"
    sv_id04 = "sv_id04"
    sv_id05 = "sv_id05"
    sv_id06 = "sv_id06"
    sv_id07 = "sv_id07"
    sv_id08 = "sv_id08"
    sv_id09 = "sv_id09"
    sv_id10 = "sv_id10"
    sv_id11 = "sv_id11"
    sv_id12 = "sv_id12"
    pdop = "pdop"
    vdop = "vdop"

    # RMC
    status = "status"
    spd_over_grnd = "spd_over_grnd"
    true_course = "true_course"
    date = "date"
    mag_variation = "mag_variation"
    mag_variation_dir = "mag_variation_dir"

    # VHW
    """ Water Speed and Heading
    """
    
    heading_true =  'heading_true'
    true = 'true'
    heading_magnetic = 'heading_magnetic'
    magnetic = 'magnetic'
    water_speed_knots = 'water_speed_knots'
    knots = 'knots'
    water_speed_km = 'water_speed_km'
    kilometers = 'kilometers'

    #VTG
    true_track = "true_track"
    true_track_sym = "true_track_sym"
    mag_track = "mag_track"
    mag_track_sym = "mag_track_sym"
    spd_over_grnd_kts = "spd_over_grnd_kts"
    spd_over_grnd_kts_sym = "spd_over_grnd_kts_sym"
    spd_over_grnd_kmph = "spd_over_grnd_kmph"
    spd_over_grnd_kmph_sym = "spd_over_grnd_kmph_sym"
    faa_mode = "faa_mode"

    # HDT
    heading = "heading"
    hdg_true = "hdg_true"

    # GLL
    status = 'status' # contains the 'A' or 'V' flag
    faa_mode = "faa_mode"

    # ZDA
    day = "day" # 01 to 31
    month = "month" # 01 to 12
    year= "year" # Year = YYYY
    local_zone = "local_zone" # 00 to +/- 13 hours
    local_zone_minutes = "local_zone_minutes" # same sign as hours

    # MWD

    direction_true = "direction_true"
    direction_magnetic = "direction_magnetic"
    wind_speed_knots = "wind_speed_knots"
    wind_speed_meters = "wind_speed_meters"
    meters = "meters"
    
    # MWV
    wind_angle = "wind_angle" # in relation to vessel's centerline
    reference = "reference" # relative (R)/true(T)
    wind_speed = "wind_speed"
    wind_speed_units = "wind_speed_units" # K/M/N

    # MTW
    temperature = "temperature"
    units = "units"

    # DPT
    depth = 'depth'
    offset = 'offset'
    range = 'range'

    # DBT
     
    unit_feet = "unit_feet"
    depth_meters = "depth_meters"
    unit_meters = "unit_meters"
    unit_fathoms = "unit_fathoms"

    # DBS

    depth_feet = 'depth_feet'
    feets = 'feets'
    depth_meter = 'depth_meter'
    depth_fathoms = 'depth_ fathoms'
    fathoms = 'fathoms'

    # RPM

    source = "source" #S = Shaft, E = Engine
    engine_no = "engine_no"
    speed = "speed" #RPM
    pitch = "pitch" #- means astern

attributes = {
    "GGA" : [Attributes.timestamp, Attributes.lat, Attributes.lat_dir, Attributes.lon, Attributes.lon_dir, Attributes.gps_qual, Attributes.num_sats, Attributes.hdop, Attributes.altitude, Attributes.altitude_units, Attributes.geo_sep, Attributes.geo_sep_units, Attributes.gps_diff_age, Attributes.ref_station_id],

    "GSA" : [ Attributes.mode, Attributes.mode_fix, Attributes.sv_id01, Attributes.sv_id02, Attributes.sv_id03, Attributes.sv_id04, Attributes.sv_id05, Attributes.sv_id06, Attributes.sv_id07, Attributes.sv_id08, Attributes.sv_id09, Attributes.sv_id10, Attributes.sv_id11, Attributes.sv_id12, Attributes.pdop, Attributes.hdop, Attributes.vdop],

    "RMC" : [Attributes.timestamp, Attributes.status, Attributes.lat, Attributes.lat_dir, Attributes.lon, Attributes.lon_dir, Attributes.spd_over_grnd, Attributes.true_course, Attributes.date, Attributes.mag_variation, Attributes.mag_variation_dir],

    "VHW": [Attributes.heading_true, Attributes.true, Attributes.heading_magnetic, Attributes.magnetic, Attributes.water_speed_knots, Attributes.knots, Attributes.water_speed_km, Attributes.kilometers],

    "VTG": [Attributes.true_track, Attributes.true_track_sym, Attributes.mag_track, Attributes.mag_track_sym, Attributes.spd_over_grnd_kts, Attributes.spd_over_grnd_kts_sym, Attributes.spd_over_grnd_kmph, Attributes.spd_over_grnd_kmph_sym, Attributes.faa_mode],

    "HDT": [Attributes.heading, Attributes.hdg_true],
  
    "GLL": [Attributes.lat, Attributes.lat_dir, Attributes.lon, Attributes.lon_dir, Attributes.timestamp, Attributes.status, Attributes.faa_mode],

    "ZDA": [Attributes.timestamp, Attributes.day, Attributes.month, Attributes.year, Attributes.local_zone, Attributes.local_zone_minutes],

    "MWD": [Attributes.direction_true, Attributes.true, Attributes.direction_magnetic, Attributes.magnetic, Attributes.wind_speed_knots, Attributes.knots, Attributes.wind_speed_meters, Attributes.meters],

    "MWV": [Attributes.wind_angle, Attributes.reference, Attributes.wind_speed, Attributes.wind_speed_units, Attributes.status],

    "MTW": [Attributes.temperature, Attributes.units],

    "DPT": [Attributes.depth, Attributes.offset, Attributes.range],

    "DBT": [Attributes.depth_feet, Attributes.unit_feet, Attributes.depth_meters, Attributes.unit_meters, Attributes.depth_fathoms, Attributes.unit_fathoms],

    "DBS": [Attributes.depth_feet, Attributes.feets, Attributes.depth_meter, Attributes.meters, Attributes.depth_fathoms, Attributes.fathoms],

    "RPM": [Attributes.source, Attributes.engine_no, Attributes.speed, Attributes.pitch, Attributes.status]
    
    }


def help():
    print(attributes)

if __name__ == "__main__":
    help()