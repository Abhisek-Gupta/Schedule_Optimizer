USE IITP_Timetable;
SHOW TABLES;
SELECT * FROM course ORDER BY Type;

-- UG First Year 2nd Sem common courses
INSERT INTO course VALUE('MA1201', 'MATH', 3, 1, 0, 'COMMON');
INSERT INTO course VALUE('PH1201', 'PHY', 3, 1, 3, 'COMMON');
INSERT INTO course VALUE ('CH1201', 'CHM', 3,1 , 3, 'COMMON');
INSERT INTO course VALUE ('IK1201', 'IKS', 3, 0, 0, 'COMMON');
INSERT INTO course VALUE ('CS1201', 'CSE', 3, 0, 3, 'COMMON');
INSERT INTO course VALUE ('EE1201', 'EE', 3, 0, 3, 'COMMON');
INSERT INTO course VALUE('ME1201', 'ME', 0, 0, 3, 'COMMON');
INSERT INTO course VALUE('ME1202', 'ME', 3, 1, 0, 'COMMON');
INSERT INTO course VALUE ('CE1201', 'CEE', 1, 0, 3, 'COMMON');

-- UG 2nd Year 2nd Sem Courses
INSERT INTO course VALUES ('CS2201', 'CSE', 3, 0, 0, 'DC'), ('CS2202', 'CSE', 3, 0, 2, 'DC'), ('CS2203', 'CSE', 3, 0, 3, 'DC'), ('CS2204', 'CSE', 0, 2, 2, 'DC'), ('CS2205', 'CSE', 3, 0, 3, 'DC'), ('CS2206', 'CSE', 3, 0, 3, 'DC'), ('CS2207', 'CSE', 3, 0, 0, 'IDE');
INSERT INTO course VALUES ('EC2201', 'EE', 3, 0, 2, 'DC'), ('EC2202', 'EE', 2, 0, 2, 'DC'), ('EC2203', 'EE', 3, 0, 0, 'DC'), ('EC2204', 'EE', 3, 0, 0, 'DC');
INSERT INTO course VALUES ('EE2201', 'EE', 3, 0, 2, 'DC'), ('EE2202', 'EE', 2, 0, 2, 'DC');
INSERT INTO course VALUES ('ME2201', 'ME', 3, 1, 2, 'DC'), ('ME2202', 'ME', 3, 1, 2, 'DC'), ('ME2203', 'ME', 3, 1, 0, 'DC'), ('ME2204', 'ME', 3, 0, 2, 'DC'), ('ME2205', 'ME', 3, 0, 0, 'IDE');
INSERT INTO course VALUES ('CE2201', 'CEE', 3, 0, 2, 'DC'), ('CE2202', 'CEE', 3, 0, 2, 'DC'), ('CE2203', 'CEE', 3, 0, 2, 'DC'), ('CE2204', 'CEE', 3, 0, 0, 'DC'), ('CE2205', 'CEE', 3, 0, 0, 'DC'), ('CE2206', 'CEE', 3, 0, 0, 'IDE');
INSERT INTO course VALUES ('CB2201', 'CBE', 2, 0, 3, 'DC'), ('CB2202', 'CBE', 3, 0, 0, 'DC'), ('CB2203', 'CBE', 3, 0, 0, 'DC'), ('CB2204', 'CBE', 3, 0, 2, 'DC'), ('CB2205', 'CBE', 3, 0, 0, 'DC'), ('CB2206', 'CBE', 3, 0, 0, 'IDE');
INSERT INTO course VALUES ('MM2201', 'MME', 3, 1, 0, 'DC'), ('MM2202', 'MME', 3, 0, 3, 'DC'), ('MM2203', 'MME', 3, 1, 0, 'DC'), ('MM2204', 'MME', 3, 0, 3, 'DC'), ('MM2205', 'MME', 3, 0, 0, 'DC'), ('MM2206', 'MME', 3, 0, 0, 'IDE');
INSERT INTO course VALUES ('MA2201', 'MATH', 2, 0, 2, 'DC'), ('MA2202', 'MATH', 3, 0, 0, 'DC'), ('MA2203', 'MATH', 3, 0, 2, 'DC'), ('MA2204', 'MATH', 3, 0, 3, 'DC'), ('MA2205', 'MATH', 3, 0, 3, 'DC'), ('MA2207', 'MATH', 3, 0, 0, 'IDE');
INSERT INTO course VALUES ('EP2201', 'PHY', 2, 1, 0, 'DC'), ('EP2202', 'PHY', 3, 1, 0, 'DC'), ('EP2203', 'PHY', 3, 1, 0, 'DC'), ('EP2204', 'PHY', 2, 1, 0, 'DC'), ('EP2205', 'PHY', 2, 0, 3, 'DC');
INSERT INTO course VALUES ('CH2201', 'CHM', 3, 0, 0, 'DC'), ('CH2202', 'CHM', 3, 1, 0, 'DC'), ('CH2203', 'CHM', 3, 1, 0, 'DC'), ('CH2204', 'CHM', 3, 0, 0, 'DC'), ('CH2205', 'CHM', 0, 0, 6, 'DC'), ('CH2206', 'CHM', 3, 0, 0, 'IDE');
INSERT INTO course VALUES ('HS2201', 'HSS', 3, 1, 0, 'DC'), ('HS2202', 'HSS', 3, 1, 0, 'DC'), ('HS2203', 'HSS', 3, 1, 0, 'DC'), ('HS2204', 'HSS', 3, 1, 0, 'DC'), ('HS2205', 'HSS', 3, 0, 0, 'IDE'), ('HS2206', 'HSS', 3, 0, 0, 'IDE'), ('HS2208', 'HSS', 3, 0, 0, 'IDE'), ('HS2209', 'HSS', 2, 1, 0, 'MBA');

-- UG 3rd Year 2nd Sem Courses
INSERT INTO course VALUES ('CS3201', 'CSE', 3, 0, 2, 'DC'), ('CS3202', 'CSE', 3, 0, 3, 'DC'), ('CS3203', 'CSE', 3, 0, 3, 'DC'), ('CS3204', 'CSE', 3, 0, 3, 'DC'), ('CS3205', 'CSE', 3, 0, 0, 'DE1'), ('CS3206', 'CSE', 3, 0, 0, 'DE1');
INSERT INTO course VALUES ('EC3201', 'EE', 3, 0, 2, 'DC'), ('EC3202', 'EE', 3, 0, 2, 'DC'), ('EC3203', 'EE', 3, 0, 0, 'DC'), ('EC3204', 'EE', 3, 0, 0, 'DC'), ('EC3205', 'EE', 3, 0, 0, 'DC'), ('EC3206', 'EE', 3, 0, 0, 'DC');
INSERT INTO course VALUES ('EE3201', 'EE', 3, 0, 2, 'DC'), ('EE3202', 'EE', 3, 0, 2, 'DC'), ('EE3203', 'EE', 3, 0, 2, 'DC'), ('EE3204', 'EE', 1, 0, 2, 'DC');
INSERT INTO course VALUES ('ME3201', 'ME', 3, 1, 2, 'DC'), ('ME3202', 'ME', 3, 1, 2, 'DC'), ('ME3203', 'ME', 3, 0, 3, 'DC'), ('ME3204', 'ME', 3, 1, 0, 'DC'), ('ME3205', 'ME', 0, 0, 4, 'DC');
INSERT INTO course VALUES ('CE3201', 'CEE', 3, 1, 0, 'DC'), ('CE3202', 'CEE', 1, 2, 0, 'DC'), ('CE3203', 'CEE', 3, 0, 0, 'DC'), ('CE3204', 'CEE', 3, 1, 0, 'DC'), ('CE3205', 'CEE', 3, 0, 2, 'DC'), ('CE3206', 'CEE', 3, 0, 0, 'DC');
INSERT INTO course VALUES ('CB3201', 'CBE', 3, 0, 0, 'DC'), ('CB3202', 'CBE', 3, 1, 0, 'DC'), ('CB3203', 'CBE', 3, 1, 0, 'DC'), ('CB3204', 'CBE', 1, 0, 4, 'DC'), ('CB3205', 'CBE', 3, 0, 0, 'DC'), ('CB3206', 'CBE', 3, 0, 0, 'DE1'), ('CB3207', 'CBE', 3, 0, 0, 'DE1');
INSERT INTO course VALUES ('MM3201', 'MME', 3, 0, 3, 'DC'), ('MM3202', 'MME', 3, 0, 2, 'DC'), ('MM3203', 'MME', 3, 0, 0, 'DC'), ('MM3204', 'MME', 3, 0, 0, 'DC'), ('MM3205', 'MME', 0, 0, 4, 'DC'), ('MM3206', 'MME', 0, 0, 3, 'DC');
INSERT INTO course VALUES ('MA3201', 'MATH', 3, 0, 0, 'DC'), ('MA3202', 'MATH', 3, 0, 2, 'DC'), ('MA3203', 'MATH', 3, 0, 0, 'DC'), ('MA3204', 'MATH', 3, 0, 2, 'DC'), ('MA3205', 'MATH', 3, 0, 0, 'DC'), ('MA3206', 'MATH', 3, 0, 2, 'DC');
INSERT INTO course VALUES ('EP3201', 'PHY', 2, 1, 0, 'DC'), ('EP3202', 'PHY', 1, 0, 4, 'DC'), ('EP3203', 'PHY', 3, 1, 2, 'DC'), ('EP3204', 'PHY', 3, 0, 0, 'DC'), ('PH3201', 'PHY', 3, 0, 0, 'DE1'), ('PH3202', 'PHY', 3, 0, 0, 'DE1'), ('PH3206', 'PHY', 3, 0, 0, 'DE2'), ('PH3209', 'PHY', 2, 1, 0, 'DE2');
INSERT INTO course VALUES ('CH3201', 'CHM', 3, 0, 0, 'DC'), ('CH3202', 'CHM', 3, 0, 0, 'DC'), ('CH3203', 'CHM', 3, 0, 2, 'DC'), ('CH3204', 'CHM', 3, 0, 0, 'DC'), ('CH3205', 'CHM', 3, 0, 2, 'DC'), ('CH3206', 'CHM', 3, 0, 0, 'DE'), ('CH3207', 'CHM', 3, 0, 0, 'DE');
INSERT INTO course VALUES ('HS3201', 'HSS', 3, 1, 2, 'DC'), ('HS3202', 'HSS', 3, 1, 0, 'DC'), ('HS3203', 'HSS', 3, 3, 0, 'DC'), ('HS3204', 'HSS', 3, 1, 0, 'DC'), ('HS3205', 'HSS', 3, 0, 0, 'DC');

-- UG 4th Year 2nd Sem Courses
INSERT INTO course VALUES ('CS4201', 'CSE', 3, 0, 0, 'DE4'), ('CS4202', 'CSE', 3, 0, 0, 'DE4'), ('CS4205', 'CSE', 3, 0, 0, 'DE5'), ('CS4206', 'CSE', 3, 0, 0, 'DE5'), ('CS4210', 'CSE', 3, 0, 0, 'DE6'), ('CS4211', 'CSE', 3, 0, 0, 'DE6');
INSERT INTO course VALUES ('EC4201', 'EE', 3, 0, 0, 'DE3'), ('EC4202', 'EE', 3, 0, 0, 'DE3'), ('EC4203', 'EE', 3, 0, 0, 'DE4'), ('EC4204', 'EE', 3, 0, 0, 'DE4'), ('EC4205', 'EE', 3, 0, 0, 'DE5'), ('EC4206', 'EE', 3, 0, 0, 'DE5');
INSERT INTO course VALUES ('EE4201', 'EE', 3, 0, 0, 'DE3'), ('EE4202', 'EE', 3, 0, 0, 'DE3'), ('EE4204', 'EE', 3, 0, 0, 'DE4'), ('EE4205', 'EE', 3, 0, 0, 'DE4');
INSERT INTO course VALUES ('ME4201', 'ME', 3, 0, 0, 'DE3'), ('ME4202', 'ME', 3, 0, 0, 'DE3'), ('ME4204', 'ME', 3, 0, 0, 'DE4'), ('ME4205', 'ME', 3, 0, 0, 'DE4'), ('ME4207', 'ME', 3, 0, 0, 'DE5'), ('ME4208', 'ME', 3, 0, 0, 'DE5');
INSERT INTO course VALUES ('CE4201', 'CEE', 3, 0, 0, 'DE3'), ('CE4202', 'CEE', 3, 0, 0, 'DE3'), ('CE4208', 'CEE', 3, 0, 0, 'DE4'), ('CE4209', 'CEE', 3, 0, 0, 'DE4'), ('CE4214', 'CEE', 3, 0, 0, 'DE5'), ('CE4215', 'CEE', 3, 0, 0, 'DE5');
INSERT INTO course VALUES ('CB4201', 'CBE', 3, 0, 0, 'DE4'), ('CB4202', 'CBE', 3, 0, 0, 'DE4'), ('CB4204', 'CBE', 3, 0, 0, 'DE5'), ('CB4205', 'CBE', 3, 0, 0, 'DE5'), ('CB4207', 'CBE', 3, 0, 0, 'DE6'), ('CB4208', 'CBE', 3, 0, 0, 'DE6');
INSERT INTO course VALUES ('MM4201', 'MME', 3, 0, 0, 'DE3'), ('MM4202', 'MME', 3, 0, 0, 'DE3'), ('MM4203', 'MME', 3, 0, 0, 'DE4'), ('MM4204', 'MME', 3, 0, 0, 'DE4'), ('MM4205', 'MME', 3, 0, 0, 'DE5'), ('MM4206', 'MME', 3, 0, 0, 'DE5');
INSERT INTO course VALUES ('MA4201', 'MATH', 3, 0, 0, 'DE3'), ('MA4206', 'MATH', 3, 0, 0, 'DE3'), ('MA4210', 'MATH', 3, 0, 0, 'DE4'), ('MA4211', 'MATH', 3, 0, 0, 'DE4'), ('MA4214', 'MATH', 3, 0, 0, 'DE5'), ('MA4212', 'MATH', 3, 0, 0, 'DE5');
INSERT INTO course VALUES ('PH4205', 'PHY', 3, 0, 0, 'DE4'), ('PH4206', 'PHY', 3, 0, 0, 'DE4'), ('PH4212', 'PHY', 3, 0, 0, 'DE5'), ('PH4213', 'PHY', 3, 0, 0, 'DE5'), ('PH4216', 'PHY', 3, 0, 0, 'DE6'), ('PH4217', 'PHY', 3, 0, 0, 'DE6'), ('PH4220', 'PHY', 3, 0, 0, 'DE7'), ('PH4221', 'PHY', 3, 0, 0, 'DE7');
INSERT INTO course VALUES ('CH4207', 'CHM', 3, 0, 0, 'DE4'), ('CH4208', 'CHM', 3, 0, 0, 'DE4'), ('CH4209', 'CHM', 3, 0, 0, 'DE5'), ('CH4210', 'CHM', 3, 0, 0, 'DE5'), ('CH4211', 'CHM', 3, 0, 0, 'DE6'), ('CH4212', 'CHM', 3, 0, 0, 'DE6');
INSERT INTO course VALUES ('HS4201', 'HSS', 3, 0, 0, 'DE3'), ('HS4206', 'HSS', 3, 0, 0, 'DE3'), ('HS4208', 'HSS', 3, 0, 0, 'DE3'), ('HS4202', 'HSS', 3, 0, 0, 'DE4'), ('HS4207', 'HSS', 3, 0, 0, 'DE4'), ('HS4209', 'HSS', 3, 0, 0, 'DE4');

-- MSc 1st Year 2nd Sem Courses
INSERT INTO course VALUES ('MA4202', 'MATH', 3, 0, 2, 'DC'), ('MA4203', 'MATH', 3, 1, 0, 'DC'), ('MA4204', 'MATH', 3, 0, 2, 'DC'), ('MA4205', 'MATH', 3, 0, 0, 'DC');
INSERT INTO course VALUES ('PH4201', 'PHY', 3, 1, 0, 'DC'), ('PH4202', 'PHY', 3, 1, 0, 'DC'), ('PH4203', 'PHY', 3, 0, 4, 'DC'), ('PH4204', 'PHY', 3, 0, 0, 'DC');
INSERT INTO course VALUES ('CH4201', 'CHM', 3, 1, 0, 'DC'), ('CH4202', 'CHM', 3, 0, 0, 'DC'), ('CH4203', 'CHM', 3, 0, 0, 'DC'), ('CH4204', 'CHM', 3, 0, 0, 'DC'), ('CH4205', 'CHM', 3, 1, 0, 'DC'), ('CH4206', 'CHM', 0, 0, 6, 'DC');

-- MSc 2nd Year 2nd Sem Courses
INSERT INTO course VALUES ('IK5201', 'IKS', 2, 0, 0, 'COMMON');
INSERT INTO course VALUES ('PH5201', 'PHY', 0, 0, 4, 'DC');
INSERT INTO course VALUES ('CH6201', 'CHM', 2, 0, 2, 'DC');
INSERT INTO course VALUES ('PH5205', 'PHY', 2, 1, 0, 'DE3'), ('PH5207', 'PHY', 3, 0, 0, 'DE3'), ('PH5218', 'PHY', 2, 1, 0, 'DE4'), ('PH5220', 'PHY', 2, 1, 0, 'DE4'), ('PH5222', 'PHY', 2, 1, 0, 'DE4');
INSERT INTO course VALUES ('CH6202', 'CHM', 3, 0, 0, 'DE2'), ('CH6209', 'CHM', 3, 0, 0, 'DE2');
INSERT INTO course VALUES ('MA6202', 'MATH', 3, 0, 0, 'DE2'), ('MA6206', 'MATH', 3, 0, 0, 'DE2'), ('MA6207', 'MATH', 3, 0, 0, 'DE3'), ('MA6208', 'MATH', 3, 0, 0, 'DE3'), ('MA6211', 'MATH', 3, 0, 0, 'DE4'), ('MA6215', 'MATH', 3, 0, 0, 'DE4');
INSERT INTO course VALUES ('MA6218', 'MATH', 3, 0, 0, 'IDE'), ('PH6201', 'PHY', 3, 0, 0, 'IDE'), ('CH6210', 'CHM', 3, 0, 0, 'IDE');

-- MTech 1st Year 2nd Sem Courses
INSERT INTO course VALUES ('RM6201', 'RM', 3, 1, 0, 'COMMON');
INSERT INTO course VALUES ('CS5201', 'CSE', 3, 0, 0, 'DC'), ('CS5202', 'CSE', 3, 0, 0, 'DC'), ('CS5203', 'CSE', 3, 0, 0, 'DC'), ('CS5204', 'CSE', 0, 1, 2, 'DC'), ('CS5205', 'CSE', 0, 1, 2, 'DC'), ('CS6202', 'CSE', 3, 0, 0, 'DE3'), ('CS6203', 'CSE', 3, 0, 0, 'DE3'), ('CS6206', 'CSE', 3, 0, 0, 'DE4'), ('CS6207', 'CSE', 3, 0, 0, 'DE4'), ('CS6209', 'CSE', 3, 0, 0, 'DE5'), ('CS6210', 'CSE', 3, 0, 0, 'DE5');
INSERT INTO course VALUES ('EC5203', 'EE', 3, 0, 2, 'DC'), ('EC5204', 'EE', 3, 0, 2, 'DC'), ('EC5201', 'EE', 3, 0, 2, 'DC'), ('EC5202', 'EE', 3, 0, 2, 'DC'), ('EE5201', 'EE', 3, 0, 2, 'DC'), ('EE5202', 'EE', 3, 0, 2, 'DC'), ('EC5214', 'EE', 3, 0, 0, 'DE3'), ('EC5215', 'EE', 3, 0, 0, 'DE3'), ('EC5216', 'EE', 3, 0, 0, 'DE4'), ('EC5217', 'EE', 3, 0, 0, 'DE4'), ('EC5218', 'EE', 3, 0, 0, 'DE5'), ('EC5219', 'EE', 3, 0, 0, 'DE5');
INSERT INTO course VALUES ('EC5205', 'EE', 3, 0, 0, 'DE3'), ('EC5206', 'EE', 3, 0, 0, 'DE3'), ('EC5209', 'EE', 3, 0, 0, 'DE5'), ('EC5210', 'EE', 3, 0, 0, 'DE5'), ('EC6203', 'EE', 3, 0, 0, 'DE4'), ('EC6204', 'EE', 3, 0, 0, 'DE4'), ('EE5203', 'EE', 3, 0, 0, 'DE3'), ('EE6201', 'EE', 3, 0, 0, 'DE3'), ('EE6213', 'EE', 3, 0, 0, 'DE4'), ('EE6214', 'EE', 3, 0, 0, 'DE4'), ('EE6216', 'EE', 3, 0, 0, 'DE5'), ('EC6217', 'EE', 3, 0, 0, 'DE5');
INSERT INTO course VALUES ('ME5201', 'ME', 1, 0, 4, 'DC'), ('ME5202', 'ME', 3, 1, 0, 'DC'), ('ME5203', 'ME', 3, 0, 0, 'DC'), ('ME5204', 'ME', 0, 0, 3, 'DC'), ('ME5205', 'ME', 3, 1, 0, 'DC'), ('ME5206', 'ME', 0, 0, 3, 'DC'), ('ME5207', 'ME', 3, 1, 0, 'DC'), ('ME5208', 'ME', 0, 0, 3, 'DC');
INSERT INTO course VALUES ('ME6215', 'ME', 3, 0, 0, 'DE3'), ('ME6208', 'ME', 3, 0, 0, 'DE3'), ('ME6203', 'ME', 3, 0, 0, 'DE3'), ('ME6210', 'ME', 3, 0, 0, 'DE4'), ('ME6212', 'ME', 3, 0, 0, 'DE4'), ('ME6206', 'ME', 3, 0, 0, 'DE4'), ('ME6209', 'ME', 3, 0, 0, 'DE3'), ('ME6202', 'ME', 3, 0, 0, 'DE3'), ('ME6204', 'ME', 3, 0, 0, 'DE4'), ('ME6205', 'ME', 3, 0, 0, 'DE4');
INSERT INTO course VALUES ('CE5201', 'CEE', 3, 0, 0, 'DC'), ('CE5202', 'CEE', 3, 0, 2, 'DC'), ('CE5203', 'CEE', 3, 0, 0, 'DC'), ('CE5204', 'CEE', 3, 0, 0, 'DC'), ('CE5205', 'CEE', 3, 0, 2, 'DC'), ('CE5206', 'CEE', 3, 0, 0, 'DC'), ('CE5207', 'CEE', 3, 0, 2, 'DC'), ('CE5208', 'CEE', 3, 0, 0, 'DC'), ('CE5209', 'CEE', 3, 0, 2, 'DC'), ('CE5210', 'CEE', 3, 0, 2, 'DC'), ('CE5211', 'CEE', 3, 0, 0, 'DC'), ('CE5212', 'CEE', 3, 0, 3, 'DC'), ('CE5213', 'CEE', 3, 0, 0, 'CE'), ('CE5214', 'CEE', 2, 1, 0, 'DC');
INSERT INTO course VALUES ('CE6222', 'CEE', 3, 0, 0, 'DE3'), ('CE6218', 'CEE', 3, 0, 0, 'DE3'), ('CE6210', 'CEE', 3, 0, 0, 'DE4'), ('CE5217', 'CEE', 3, 0, 0, 'DE4'), ('CE6229', 'CEE', 3, 0, 0, 'DE4'), ('CE6203', 'CEE', 3, 0, 0, 'DE3'), ('CE6204', 'CEE', 3, 0, 0, 'DE3'), ('CE6228', 'CEE', 3, 0, 0, 'DE3'), ('CE6211', 'CEE', 3, 0, 0, 'DE3');
INSERT INTO course VALUES ('CB5201', 'CBE', 3, 1, 0, 'DC'), ('CB5202', 'CBE', 3, 1, 0, 'DC'), ('CB5203', 'CBE', 1, 0, 3, 'DC'), ('CB6204', 'CBE', 3, 0, 0, 'DE3'), ('CB6205', 'CBE', 3, 0, 0, 'DE4'), ('CB6203', 'CBE', 3, 0, 0, 'DE3'), ('CB6206', 'CBE', 3, 0, 0, 'DE4');
INSERT INTO course VALUES ('MM5201', 'MME', 3, 0, 2, 'DC'), ('MM5202', 'MME', 3, 0, 2, 'DC'), ('MM6201', 'MME', 3, 0, 0, 'DE2'), ('MM6202', 'MME', 3, 0, 0, 'DE2'), ('MM6204', 'MME', 3, 0, 0, 'DE3'), ('MM6205', 'MME', 3, 0, 0, 'DE3'), ('MM6209', 'MME', 3, 0, 0, 'DE4'), ('MM6210', 'MME', 3, 0, 0, 'DE4');
INSERT INTO course VALUES ('MC5201', 'MATH', 3, 0, 0, 'DC'), ('MC5202', 'MATH', 2, 0, 2, 'DC'), ('MC5203', 'MATH', 0, 1, 2, 'DC'), ('MA5201', 'MATH', 3, 0, 0, 'DE4');

-- MTech 2nd Year 2nd Sem Courses