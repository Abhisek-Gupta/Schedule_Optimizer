-- Classrooms

USE IITP_Timetable;
SHOW TABLES;
SELECT * FROM IITP_Timetable.classrooms_labs ORDER BY Department ASC, Type ASC;

INSERT INTO IITP_Timetable.classrooms_labs VALUES ('LT003', 270, 'CLASSROOM', 'COMMON'), ('LT103', 270, 'CLASSROOM', 'COMMON');
INSERT INTO IITP_Timetable.classrooms_labs VALUES ('LT001', 180, 'CLASSROOM', 'CSE'), ('LT002', 120, 'CLASSROOM', 'CSE'), ('CS001', 60, 'CLASSROOM', 'CSE');
INSERT INTO IITP_Timetable.classrooms_labs VALUES ('LT101', 180, 'CLASSROOM', 'EE'), ('LT102', 120, 'CLASSROOM', 'EE'), ('R205', 80, 'CLASSROOM', 'EE'), ('EE001', 60, 'CLASSROOM', 'EE');
INSERT INTO IITP_Timetable.classrooms_labs VALUES ('R502', 180, 'CLASSROOM', 'ME'), ('R308', 120, 'CLASSROOM', 'ME'), ('R304', 80, 'CLASSROOM', 'ME'), ('ME001', 60, 'CLASSROOM', 'ME');
INSERT INTO IITP_Timetable.classrooms_labs VALUES ('R104', 160, 'CLASSROOM', 'CEE'), ('R105', 80, 'CLASSROOM', 'CEE'), ('R107', 160, 'CLASSROOM', 'CEE'), ('CE001', 60, 'CLASSROOM', 'CEE');
INSERT INTO IITP_Timetable.classrooms_labs VALUES ('R307', 80, 'CLASSROOM', 'CBE'), ('R310', 160, 'CLASSROOM', 'CBE'), ('CB001', 60, 'CLASSROOM', 'CBE');
INSERT INTO IITP_Timetable.classrooms_labs VALUES ('R106', 80, 'CLASSROOM', 'MME'), ('R109', 160, 'CLASSROOM', 'MME'), ('MM001', 60, 'CLASSROOM', 'MME');
INSERT INTO IITP_Timetable.classrooms_labs VALUES ('R301', 60, 'CLASSROOM', 'MATH'), ('R303', 160, 'CLASSROOM', 'MATH'), ('MA001', 60, 'CLASSROOM', 'MATH');
INSERT INTO IITP_Timetable.classrooms_labs VALUES ('R101', 60, 'CLASSROOM', 'PHY'), ('R102', 160, 'CLASSROOM', 'PHY'), ('R103', 60, 'CLASSROOM', 'PHY'), ('PH001', 60, 'CLASSROOM', 'PHY');
INSERT INTO IITP_Timetable.classrooms_labs VALUES ('R305', 60, 'CLASSROOM', 'CHM'), ('R306', 60, 'CLASSROOM', 'CHM'), ('CH001', 60, 'CLASSROOM', 'CHM');
INSERT INTO IITP_Timetable.classrooms_labs VALUES ('R302', 60, 'CLASSROOM', 'HSS'), ('HS001', 60, 'CLASSROOM', 'HSS');

INSERT INTO IITP_Timetable.classrooms_labs VALUES ('CC1', 160, 'LAB', 'CSE'), ('CSLAB', 80, 'LAB', 'CSE'), ('HDWLAB', 120, 'LAB', 'CSE');
INSERT INTO IITP_Timetable.classrooms_labs VALUES ('EELAB1', 80, 'LAB', 'EE'), ('EELAB2', 80, 'LAB', 'EE'), ('EEWORKSHOP', 120, 'LAB', 'EE');
INSERT INTO IITP_Timetable.classrooms_labs VALUES ('MELAB1', 80, 'LAB', 'ME'), ('MELAB2', 80, 'LAB', 'ME'), ('MEWORKSHOP', 120, 'LAB', 'ME');
INSERT INTO IITP_Timetable.classrooms_labs VALUES ('CEWORKSHOP', 120, 'LAB', 'CEE'), ('CELAB1', 120, 'LAB', 'CEE'), ('CELAB2', 120, 'LAB', 'CEE');
INSERT INTO IITP_Timetable.classrooms_labs VALUES ('CBLAB1', 80, 'LAB', 'CBE'), ('CBWORKSHOP', 120, 'LAB', 'CBE');
INSERT INTO IITP_Timetable.classrooms_labs VALUES ('MMELAB1', 80, 'LAB', 'MME'), ('MMWORKSHOP', 120, 'LAB', 'MME');
INSERT INTO IITP_Timetable.classrooms_labs VALUES ('MALAB1', 80, 'LAB', 'MATH');
INSERT INTO IITP_Timetable.classrooms_labs VALUES ('PHLAB1', 80, 'LAB', 'PHY'), ('PHLAB2', 80, 'LAB', 'PHY');
INSERT INTO IITP_Timetable.classrooms_labs VALUES ('CHLAB1', 80, 'LAB', 'CHM'), ('CHLAB2', 80, 'LAB', 'CHM');

