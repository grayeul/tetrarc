PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE users (
	id INTEGER NOT NULL, 
	username VARCHAR NOT NULL, 
	name VARCHAR NOT NULL, 
	email VARCHAR NOT NULL, 
	created DATETIME NOT NULL, 
	pending_approval INTEGER NOT NULL, 
	password VARCHAR, 
	last_login DATETIME, 
	disabled INTEGER NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT "uniqUsername" UNIQUE (username), 
	CONSTRAINT "uniqEmail" UNIQUE (email)
);
INSERT INTO users VALUES(1,'system','System User','system@rockylinux.org','2026-03-24 16:27:25',1,NULL,NULL,0);
INSERT INTO users VALUES(2,'rocky','rocky','bob@rockylinux.org','2026-03-24 16:28:28',0,X'24326224313524513776734d674246666672752f314f4966364f6d4875795846396750305767773774577841314d386a704d744d6a7a686e2e57694b',NULL,0);
INSERT INTO users VALUES(3,'rocky_a','Mr. Admin','rocky_a@rockylinux.org','2026-04-08 22:00:33',0,X'243262243135245a6a736f714c48474c51656c747971472f6e4b61694f6a6c61754648494f7654696c7a6e67396c32736552764b744c3841646d7453',NULL,0);
INSERT INTO users VALUES(4,'guest','Mr. Guest','guest@rockylinux.org','2026-04-08 22:02:58',0,X'243262243135244a77742f6b3855647535756b5969382e72356d6f3965574d69776957536f654d63554e644b525a3970504a7a78447739396c664c4f',NULL,0);
INSERT INTO users VALUES(5,'grayeul','BobR','grayeul@gmail.com','2026-04-11 17:19:19',0,X'24326224313524544d45634b344a61454e336d6a57794359594350474f4a754c4e42384a6257794b7472536158617957596353703139414c3342454f',NULL,0);
CREATE TABLE roles (
	id INTEGER NOT NULL, 
	name VARCHAR NOT NULL, 
	description VARCHAR NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT "uniqName" UNIQUE (name)
);
INSERT INTO roles VALUES(1,'admin','Full Admin Privileges - can do anything');
INSERT INTO roles VALUES(2,'tester','Can submit test reports');
INSERT INTO roles VALUES(3,'viewer','Can see results - but not submit');
INSERT INTO roles VALUES(4,'lead','Testing Lead');
CREATE TABLE test_groups (
	id INTEGER NOT NULL, 
	num INTEGER NOT NULL, 
	name VARCHAR NOT NULL, 
	description VARCHAR NOT NULL, 
	notes VARCHAR, 
	PRIMARY KEY (id), 
	CONSTRAINT "uniqName" UNIQUE (name)
);
INSERT INTO test_groups VALUES(1,1,'Community Testable Items',' Self Explanatory',NULL);
INSERT INTO test_groups VALUES(2,1,'Repository Checks',' validates repo setup',NULL);
INSERT INTO test_groups VALUES(3,1,'OpenQA Tests',' checks various installer requirements',NULL);
INSERT INTO test_groups VALUES(4,1,'Post-Installation Requirements',' things to check after install',NULL);
INSERT INTO test_groups VALUES(5,1,'Cloud Image Requirements',' other image types',NULL);
INSERT INTO test_groups VALUES(6,1,'Cloud Image Testing',' tests on those images',NULL);
INSERT INTO test_groups VALUES(7,1,'SIG/AltArch',' Raspberry PI 4/5',NULL);
INSERT INTO test_groups VALUES(8,1,'Sparky Testing',' New tests',NULL);
INSERT INTO test_groups VALUES(9,1,'Final Release',' Last steps',NULL);
INSERT INTO test_groups VALUES(10,1,'Operations',' Announcements and etc',NULL);
CREATE TABLE test_books (
	id INTEGER NOT NULL, 
	name VARCHAR NOT NULL, 
	start_date DATETIME NOT NULL, 
	target_end_date DATETIME, 
	status VARCHAR NOT NULL, 
	description VARCHAR NOT NULL, rcs JSON DEFAULT '[]', 
	PRIMARY KEY (id), 
	CONSTRAINT "uniqName" UNIQUE (name)
);
INSERT INTO test_books VALUES(1,'RockyLinux-9.7','2025-11-11 00:00:00.000000','2025-12-24 00:00:00.000000',' completed',' Version 9.7 - more stuff here','[]');
INSERT INTO test_books VALUES(2,'RockyLinux-10.1','2025-11-11 00:00:00.000000','2025-12-24 00:00:00.000000',' completed',' Version 10.1 -even more stuff for this one','[]');
INSERT INTO test_books VALUES(3,'RockyLinux-10.2','2026-05-20 00:00:00.000000','2026-06-15 00:00:00.000000',' not started',' Version 10.2 - placeholder','["RC1"]');
CREATE TABLE user_sessions (
	id INTEGER NOT NULL, 
	auth_token VARCHAR NOT NULL, 
	user_id INTEGER NOT NULL, 
	created DATETIME NOT NULL, 
	valid_until DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT "uniqUserId" UNIQUE (user_id), 
	CONSTRAINT "uniqAuthToken" UNIQUE (auth_token), 
	FOREIGN KEY(user_id) REFERENCES users (id)
);
INSERT INTO user_sessions VALUES(1,'86a60ad1-e32e-4b7e-aa7e-133383e967de',5,'2026-04-13 23:38:26.475673','2026-04-14 23:38:26.475673');
CREATE TABLE user_roles (
	id INTEGER NOT NULL, 
	user_id INTEGER NOT NULL, 
	role_id INTEGER NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT "uniqPair" UNIQUE (user_id, role_id), 
	FOREIGN KEY(user_id) REFERENCES users (id), 
	FOREIGN KEY(role_id) REFERENCES roles (id)
);
INSERT INTO user_roles VALUES(1,3,1);
INSERT INTO user_roles VALUES(2,4,3);
INSERT INTO user_roles VALUES(3,2,2);
INSERT INTO user_roles VALUES(4,5,1);
INSERT INTO user_roles VALUES(5,5,4);
CREATE TABLE basic_tests (
	id INTEGER NOT NULL, 
	name VARCHAR NOT NULL, 
	shortname VARCHAR NOT NULL, 
	test_group_id INTEGER NOT NULL, 
	testorder INTEGER NOT NULL, 
	description VARCHAR NOT NULL, 
	created DATETIME NOT NULL, 
	created_by INTEGER NOT NULL, 
	last_modified DATETIME NOT NULL, 
	last_modified_by INTEGER NOT NULL, 
	link_to_procedure VARCHAR, 
	notes VARCHAR, blocking INTEGER default 0, 
	PRIMARY KEY (id), 
	CONSTRAINT "uniqName" UNIQUE (name), 
	CONSTRAINT "uniqShortName" UNIQUE (shortname), 
	FOREIGN KEY(test_group_id) REFERENCES test_groups (id), 
	FOREIGN KEY(created_by) REFERENCES users (id), 
	FOREIGN KEY(last_modified_by) REFERENCES users (id)
);
INSERT INTO basic_tests VALUES(1,'Boot ISO Image-burn ISO to CD/DVD and test install ','BootISO',1,1,replace('For appropriate ISO''s only: boot.iso = ~800M\n','\n',char(10)),'2026-03-24 20:09:31',1,'2026-04-11 21:29:42.964127',5,' https://testing.rocky.page/documentation/QA/Testcase_Boot_Methods_Boot_Iso',NULL,1);
INSERT INTO basic_tests VALUES(2,'Media Consistency Verification - QA:Testcase Media USB Fedora Media writer - Boot ISO','MediaCheck',1,2,replace('This means that the installer’s mechanism for verifying the install medium is intact and must complete successfully, with the assumption that the medium was correctly written and a successful boot and install are possible. It should return a failure message if this not the case.\n','\n',char(10)),'2026-03-24 20:09:31',1,'2026-04-11 22:10:03.594129',5,' https://testing.rocky.page/documentation/QA/Testcase_Media_USB_dd',NULL,1);
INSERT INTO basic_tests VALUES(3,'No Broken Packages-Repoclosure','Repoclosure',2,1,'Critical errors, such as undeclared conflicts, unresolved dependencies, or modules relying on packages from another stream will be considered an automatic blocker. There are potential exceptions to this (eg, freeradius cannot be installed on an older perl stream, this is a known issue upstream).','2026-03-25 16:04:53',1,'2026-04-07 10:45:30.768625',2,'https://testing.rocky.page/documentation/QA/Testcase_Media_Repoclosure/',NULL,0);
INSERT INTO basic_tests VALUES(4,' Media Consistency Verification - QA:Testcase Media USB Fedora Media writer - Minimal ISO','MediaCheck-Minimal',1,3,' This means that the installer’s mechanism for verifying the install medium is intact and must complete successfully, with the assumption that the medium was correctly written and a successful boot and install are possible. It should return a failure message if this not the case.','2026-04-07 15:36:39',2,'2026-04-11 10:21:57.297219',3,NULL,NULL,0);
INSERT INTO basic_tests VALUES(5,' Media Consistency Verification - QA:Testcase Media USB Fedora Media writer - DVD ISO','MediaCheck-Full DVD',1,4,' This means that the installer’s mechanism for verifying the install medium is intact and must complete successfully, with the assumption that the medium was correctly written and a successful boot and install are possible. It should return a failure message if this not the case.','2026-04-07 15:38:06',2,'2026-04-11 21:35:00.256475',5,NULL,NULL,1);
INSERT INTO basic_tests VALUES(6,' Boot Live image - Workstation Lite','BootLive-Lite',1,5,' Boot the live image and verify basic functionality','2026-04-07 15:40:03',2,'2026-04-11 10:22:40.291667',3,NULL,NULL,0);
INSERT INTO basic_tests VALUES(7,' Boot Live image - XFCE','BootLive-XFCE',1,6,replace(' Boot the live image and verify basic functionality\n','\n',char(10)),'2026-04-07 15:41:01',2,'2026-04-07 15:41:01',2,NULL,NULL,0);
INSERT INTO basic_tests VALUES(8,' Boot Live image - MATE ','BootLive-MATE',1,7,' Boot the live image and verify basic functionality','2026-04-07 15:41:46',2,'2026-04-11 10:22:29.783218',3,NULL,NULL,0);
INSERT INTO basic_tests VALUES(9,' Boot Live image - Cinnamon','BootLive-Cinnamon',1,7,' Boot the live image and verify basic functionality','2026-04-07 15:42:31',2,'2026-04-11 10:22:50.834595',3,NULL,NULL,0);
INSERT INTO basic_tests VALUES(10,'FWUPD - Install and check','FWUPD',1,8,' Preferably test Secureboot and perform an update','2026-04-07 15:43:27',2,'2026-04-11 10:20:54.539358',3,' ',NULL,0);
INSERT INTO basic_tests VALUES(11,' No Broken Packages - QA:Testcase Media File Conflicts','MediaFileConflicts',2,2,' Critical errors, such as undeclared conflicts, unresolved dependencies, or modules relying on packages from another stream will be considered an automatic blocker. There are potential exceptions to this (eg, freeradius cannot be installed on an older perl stream, this is a known issue upstream).','2026-04-07 15:46:59',2,'2026-04-07 15:46:59',2,' https://testing.rocky.page/documentation/QA/Testcase_Media_File_Conflicts',NULL,0);
INSERT INTO basic_tests VALUES(12,' Repositories Must Match Upstream - QA:Testcase Repo Compare','Upstream Repo Match',2,3,'Repositories and the packages within them should match upstream as closely as possible. Notable exceptions would be kmods, kpatch, or what is deemed as “spyware” like insights. Packages that are available from upstream should not have hard requirements on RHSM and packages that have it default built in should be patched out.','2026-04-07 15:48:08',2,'2026-04-07 15:48:08',2,' https://testing.rocky.page/documentation/QA/Testcase_Repo_Compare',NULL,0);
INSERT INTO basic_tests VALUES(13,' Repositories Must Match Upstream - QA:Testcase Packages No Insights','No Insights Pkg',2,4,' Repositories and the packages within them should match upstream as closely as possible. Notable exceptions would be kmods, kpatch, or what is deemed as “spyware” like insights. Packages that are available from upstream should not have hard requirements on RHSM and packages that have it default built in should be patched out.','2026-04-07 15:49:18',2,'2026-04-07 15:49:18',2,' https://testing.rocky.page/documentation/QA/Testcase_Packages_No_Insights',NULL,0);
INSERT INTO basic_tests VALUES(14,' Repositories Must Match Upstream -     QA:Testcase Packages No RHSM','No RHSM Pkg',2,5,'Repositories and the packages within them should match upstream as closely as possible. Notable exceptions would be kmods, kpatch, or what is deemed as “spyware” like insights. Packages that are available from upstream should not have hard requirements on RHSM and packages that have it default built in should be patched out.','2026-04-07 15:50:52',2,'2026-04-07 15:50:52',2,' https://testing.rocky.page/documentation/QA/Testcase_Packages_No_RHSM',NULL,0);
INSERT INTO basic_tests VALUES(15,' Debranding - QA:Testcase Debranding','Debranding',2,6,'Assets and functionality that are Red Hat specific should not be included. If they are not patched out, it will be considered an automatic blocker.','2026-04-07 15:51:53',2,'2026-04-07 15:51:53',2,' https://testing.rocky.page/documentation/QA/Testcase_Debranding',NULL,0);
INSERT INTO basic_tests VALUES(16,' System Services : firewalld - QA:Testcase System Services','SystemServices: firewalld',4,2,'All system services present after installation must start properly, with the exception of services that require hardware which is not present. ','2026-04-07 15:55:00',2,'2026-04-07 15:55:05.772921',2,NULL,NULL,0);
INSERT INTO basic_tests VALUES(17,' System Services : auditd - QA:Testcase System Services','SystemServices: auditd',4,3,' All system services present after installation must start properly, with the exception of services that require hardware which is not present. ','2026-04-07 15:57:49',2,'2026-04-07 15:57:49',2,NULL,NULL,0);
INSERT INTO basic_tests VALUES(18,' System Services : chronyd - QA:Testcase System Services','SystemServices: chronyd',4,4,' All system services present after installation must start properly, with the exception of services that require hardware which is not present. ','2026-04-07 15:58:33',2,'2026-04-07 15:58:33',2,NULL,NULL,0);
INSERT INTO basic_tests VALUES(19,' Keyboard Layout - QA:Testcase Keyboard Layout','Keyboard Layout',4,5,replace('If a particular keyboard layout has been configured for the system, that layout must be used:\n\n* When unlocking storage volumes (encrypted by LUKS)\n* When logging in at a TTY console\n* When logging in via GDM\n* After logging into a GNOME desktop system, if the user does not have their own layout configuration set.','\n',char(10)),'2026-04-07 15:59:25',2,'2026-04-07 15:59:00.472167',2,NULL,NULL,0);
INSERT INTO basic_tests VALUES(20,' SELinux Errors - QA:Testcase SELinux Errors on Server installations','No SELinux Errors',4,6,' There must be no SELinux denial logs in /var/log/audit/audit.log','2026-04-07 16:00:27',2,'2026-04-07 16:00:27',2,NULL,NULL,0);
INSERT INTO basic_tests VALUES(21,' SELinux and Crash Notifications (Desktop Only) - QA:Testcase SELinux Errors on Desktop clients','SELinux Desktop Clients',4,7,' There must be no SELinux denial notifications or crash notifications on boot, during installation, or during first login.','2026-04-07 16:01:24',2,'2026-04-07 16:01:24',2,NULL,NULL,0);
INSERT INTO basic_tests VALUES(22,' Default Application Functionality (Desktop Only) - QA:Testcase Application Functionality','Default Applications',4,9,replace('Applications that can be launched within GNOME or on the command line must start successfully and withstand basic functionality tests. This includes:\n\n* Web browser\n* File manager\n* Package manager\n* Image/Document Viewers\n* Text editors (gedit, vim)\n* Archive manager\n* Terminal Emulator (gnome terminal)\n* Problem Reporter\n* Help Viewer\n* System Settings','\n',char(10)),'2026-04-07 16:02:27',2,'2026-04-07 16:00:48.368147',2,NULL,NULL,0);
INSERT INTO basic_tests VALUES(23,' Default Panel Functionality (Desktop Only) - QA:Testcase GNOME UI Functionality','Default Panel UI',4,10,replace('All elements of GNOME should function properly in regular use.\n','\n',char(10)),'2026-04-07 16:03:32',2,'2026-04-07 16:03:32',2,NULL,NULL,0);
INSERT INTO basic_tests VALUES(24,' Dual Monitor Setup (Desktop Only) - QA:Testcase Multimonitor Setup','Dual Monitor',4,11,'Computers using two monitors, the graphical output is correctly shown on both monitors','2026-04-07 16:04:16',2,'2026-04-07 16:01:50.923087',2,NULL,NULL,0);
INSERT INTO basic_tests VALUES(25,' Artwork and Assets (Server and Desktop) - QA:Testcase Artwork and Assets','Artwork',4,12,'Proposed final artwork (such as wallpapers and other assets) must be included. A wallpaper from this package should show up as a default for GDM and GNOME.','2026-04-07 16:05:02',2,'2026-04-07 16:05:02',2,NULL,NULL,0);
INSERT INTO basic_tests VALUES(26,' Packages and Module Installation - QA:Testcase Basic Package installs','Pkg + Module Installation',4,13,'Packages (non-module) should be able to be installed without conflicts or dependencies on repositories outside of Rocky Linux.','2026-04-07 16:05:55',2,'2026-04-07 16:05:55',2,NULL,NULL,0);
INSERT INTO basic_tests VALUES(27,' Packages and Module Installation - QA:Testcase Module Streams      Default modules (as listed in dnf module list) should be installed without requiring them to be enabled.     Module streams should be able to be switched and those packages should be able to be installed without errors or unresolved dependencies.','Module Functionality',4,14,replace('Default modules (as listed in dnf module list) should be installed without requiring them to be enabled.\n\nModule streams should be able to be switched and those packages should be able to be installed without errors or unresolved dependencies.','\n',char(10)),'2026-04-07 16:06:41',2,'2026-04-07 16:01:25.681725',2,NULL,NULL,0);
INSERT INTO basic_tests VALUES(28,' Identity Management (FreeIPA) - QA:Testcase Identity Management','FreeIPA',4,14,replace('It should be possible to setup a IdM server (FreeIPA), use it''s functionality and connect clients.\n\nSpecial request from Infrastructure - It is a canary of sorts to check many sub-dependency packages.\n\nBasic documentation WIP: https://github.com/rocky-linux/documentation/blob/ipa_wip/docs/books/ipa/01-master.md\n\n','\n',char(10)),'2026-04-07 16:08:15',2,'2026-04-07 16:03:26.555093',2,' https://github.com/rocky-linux/documentation/blob/ipa_wip/docs/books/ipa/01-master.md',NULL,0);
INSERT INTO basic_tests VALUES(29,' FIPS Mode is functional and working','FIPS',4,15,replace('Install in FIPS mode. Verify by:\nfips-mode-setup --check\ncat /proc/sys/crypto/fips_enabled # Should return 1\ngrep fips=1 /proc/cmdline\n','\n',char(10)),'2026-04-07 16:09:03',2,'2026-04-07 16:09:03',2,NULL,NULL,0);
INSERT INTO basic_tests VALUES(30,'Images Published for Container Base','Container Base',5,1,'Release-blocking cloud disk images must be published to appropriate cloud provider and the image must successfully boot. This also applies to KVM based instances, such as x86 and aarch64 systems.','2026-04-07 16:12:41',2,'2026-04-07 16:12:41',2,NULL,NULL,0);
INSERT INTO basic_tests VALUES(31,' Images Published for Container Minimal','Container Minimal',5,2,replace(' Release-blocking cloud disk images must be published to appropriate cloud provider and the image must successfully boot. This also applies to KVM based instances, such as x86 and aarch64 systems.\n','\n',char(10)),'2026-04-07 16:13:17',2,'2026-04-07 16:13:17',2,NULL,NULL,0);
INSERT INTO basic_tests VALUES(32,'Images Published for Container UBI','Container UBI',5,2,'Release-blocking cloud disk images must be published to appropriate cloud provider and the image must successfully boot. This also applies to KVM based instances, such as x86 and aarch64 systems.','2026-04-07 16:13:57',2,'2026-04-07 16:13:57',2,NULL,NULL,0);
INSERT INTO basic_tests VALUES(33,'Images Published for GenericCloud','Generic Cloud',5,4,'Release-blocking cloud disk images must be published to appropriate cloud provider and the image must successfully boot. This also applies to KVM based instances, such as x86 and aarch64 systems.','2026-04-07 16:15:04',2,'2026-04-07 16:15:04',2,NULL,NULL,0);
INSERT INTO basic_tests VALUES(34,'Images Published for Amazon EC2','Amazon EC2',5,5,'Release-blocking cloud disk images must be published to appropriate cloud provider and the image must successfully boot. This also applies to KVM based instances, such as x86 and aarch64 systems.','2026-04-07 16:15:58',2,'2026-04-07 16:15:58',2,NULL,NULL,0);
INSERT INTO basic_tests VALUES(35,'Images Published for Azure','Azure',5,6,'Release-blocking cloud disk images must be published to appropriate cloud provider and the image must successfully boot. This also applies to KVM based instances, such as x86 and aarch64 systems.','2026-04-07 16:17:10',2,'2026-04-07 16:17:10',2,NULL,NULL,0);
INSERT INTO basic_tests VALUES(36,'Images Published for Oracle','Oracle',5,7,'Release-blocking cloud disk images must be published to appropriate cloud provider and the image must successfully boot. This also applies to KVM based instances, such as x86 and aarch64 systems.','2026-04-07 16:17:47',2,'2026-04-07 16:17:47',2,NULL,NULL,0);
INSERT INTO basic_tests VALUES(37,'Images Published for Vagrant - libvirt','Vagrant - libvirt',5,8,'Release-blocking cloud disk images must be published to appropriate cloud provider and the image must successfully boot. This also applies to KVM based instances, such as x86 and aarch64 systems.','2026-04-07 16:18:28',2,'2026-04-07 16:18:28',2,NULL,NULL,0);
INSERT INTO basic_tests VALUES(38,'Images Published for Vagrant - VirtualBox','Vagrant-VirtualBox',5,9,'Release-blocking cloud disk images must be published to appropriate cloud provider and the image must successfully boot. This also applies to KVM based instances, such as x86 and aarch64 systems.','2026-04-07 16:19:06',2,'2026-04-07 16:19:06',2,NULL,NULL,0);
INSERT INTO basic_tests VALUES(39,'Images Published for Vagrant - VMWare','Vagrant-VMWare',5,10,'Release-blocking cloud disk images must be published to appropriate cloud provider and the image must successfully boot. This also applies to KVM based instances, such as x86 and aarch64 systems.','2026-04-07 16:19:47',2,'2026-04-07 16:19:47',2,NULL,NULL,0);
INSERT INTO basic_tests VALUES(40,'Update rockylinux.org cloud images list','Update Images List',5,11,'Update official list of Rocky Cloud Images','2026-04-07 16:20:24',2,'2026-04-07 16:20:24',2,NULL,NULL,0);
INSERT INTO basic_tests VALUES(41,'Images Tested for Container Base','ContainerBase-Test',6,1,replace('Release-blocking cloud disk images must be published to appropriate cloud provider and the image must successfully boot. This also applies to KVM based instances, such as x86 and aarch64 systems.\n','\n',char(10)),'2026-04-07 16:22:14',2,'2026-04-07 16:22:14',2,NULL,NULL,0);
INSERT INTO basic_tests VALUES(42,'Images Tested for Container Minimal','Container-Minimal-Test',6,2,replace('Release-blocking cloud disk images must be published to appropriate cloud provider and the image must successfully boot. This also applies to KVM based instances, such as x86 and aarch64 systems.\n','\n',char(10)),'2026-04-07 16:25:02',2,'2026-04-07 16:25:02',2,NULL,NULL,0);
INSERT INTO basic_tests VALUES(43,'Images Tested for Container UBI','Container UBI-Test',6,3,'Release-blocking cloud disk images must be published to appropriate cloud provider and the image must successfully boot. This also applies to KVM based instances, such as x86 and aarch64 systems.','2026-04-07 16:25:44',2,'2026-04-07 16:25:44',2,NULL,NULL,0);
INSERT INTO basic_tests VALUES(44,'Images Tested for GenericCloud','GenericCloud-Test',6,4,replace('Release-blocking cloud disk images must be published to appropriate cloud provider and the image must successfully boot. This also applies to KVM based instances, such as x86 and aarch64 systems.\n\nThis image has a history of not booting on both BIOS and UEFI - Test both!','\n',char(10)),'2026-04-07 16:27:15',2,'2026-04-07 16:04:16.949422',2,NULL,NULL,0);
INSERT INTO basic_tests VALUES(45,'Images Tested for Amazon EC2','Amazon EC2-Test',6,5,'Release-blocking cloud disk images must be published to appropriate cloud provider and the image must successfully boot. This also applies to KVM based instances, such as x86 and aarch64 systems.','2026-04-07 16:27:51',2,'2026-04-07 16:27:51',2,NULL,NULL,0);
INSERT INTO basic_tests VALUES(46,'Images Tested for Azure','Azure-Test',6,6,'Release-blocking cloud disk images must be published to appropriate cloud provider and the image must successfully boot. This also applies to KVM based instances, such as x86 and aarch64 systems.','2026-04-07 16:28:31',2,'2026-04-07 16:28:31',2,NULL,NULL,0);
INSERT INTO basic_tests VALUES(47,'Images Tested for Oracle','Oracle-Test',6,7,'Release-blocking cloud disk images must be published to appropriate cloud provider and the image must successfully boot. This also applies to KVM based instances, such as x86 and aarch64 systems.','2026-04-07 16:29:08',2,'2026-04-07 16:29:08',2,NULL,NULL,0);
INSERT INTO basic_tests VALUES(48,'Images Tested for Vagrant - libvirt','Vagrant-libvirt-Test',6,8,'Release-blocking cloud disk images must be published to appropriate cloud provider and the image must successfully boot. This also applies to KVM based instances, such as x86 and aarch64 systems.','2026-04-07 16:29:51',2,'2026-04-07 16:29:51',2,NULL,NULL,0);
INSERT INTO basic_tests VALUES(49,'Images Tested for Vagrant - VirtualBox','Vagrant-VirtualBox-Test',6,9,replace('Release-blocking cloud disk images must be published to appropriate cloud provider and the image must successfully boot. This also applies to KVM based instances, such as x86 and aarch64 systems.\n','\n',char(10)),'2026-04-07 16:30:52',2,'2026-04-07 16:30:52',2,NULL,NULL,0);
INSERT INTO basic_tests VALUES(50,'Images Tested for Vagrant - VMWare','Vagrant-VMWare-Test',6,10,replace('Release-blocking cloud disk images must be published to appropriate cloud provider and the image must successfully boot. This also applies to KVM based instances, such as x86 and aarch64 systems.\n','\n',char(10)),'2026-04-07 16:31:30',2,'2026-04-07 16:31:30',2,NULL,NULL,0);
INSERT INTO basic_tests VALUES(51,'Is there a display output','Display?',7,1,'Please verify that any external display outputs work','2026-04-07 21:37:11',2,'2026-04-07 21:37:11',2,NULL,NULL,0);
INSERT INTO basic_tests VALUES(52,'Does the device boot?','Boot OK?',7,2,'Device should boot to prompt without error','2026-04-07 21:40:24',2,'2026-04-07 21:40:24',2,NULL,NULL,0);
INSERT INTO basic_tests VALUES(53,' Can you log-in?','Login OK?',7,3,'User:rocky / password:rockylinux','2026-04-07 21:43:57',2,'2026-04-07 21:43:57',2,NULL,NULL,0);
INSERT INTO basic_tests VALUES(54,'Does sudo work?','sudo working?',7,4,'sudo ls is sufficient for this test.','2026-04-07 21:45:26',2,'2026-04-07 21:45:26',2,NULL,NULL,0);
INSERT INTO basic_tests VALUES(55,'Is the README there and correct for this device?','README present?',7,5,'cat ~/README','2026-04-07 21:46:02',2,'2026-04-07 21:46:02',2,NULL,NULL,0);
INSERT INTO basic_tests VALUES(56,'Does the expand filesystem script work?','Expand Filesystem?',7,6,'See README for details for each device','2026-04-07 21:47:25',2,'2026-04-07 21:47:25',2,NULL,NULL,0);
INSERT INTO basic_tests VALUES(57,'Can the device connect to a wireless network?','Wireless Network',7,7,replace('* `sudo nmcli radio wifi = enabled`\n* `sudo nmcli dev wifi list`\n* `sudo nmcli dev wifi connect network-ssid password "network-password"`','\n',char(10)),'2026-04-07 21:48:29',2,'2026-04-07 16:48:54.461756',2,NULL,NULL,0);
INSERT INTO basic_tests VALUES(58,'Can the device connect to ethernet RJ45 network?','Wired network',7,8,'Not valid for every device','2026-04-07 21:59:54',2,'2026-04-07 21:59:54',2,NULL,NULL,0);
INSERT INTO basic_tests VALUES(59,'Can the device get package updates?','dnf update',7,9,replace('`sudo dnf clean all && sudo dnf update`\n\nNote: depending on when this test is run, you may have to switch to the testing repos first. See channel for details.\n','\n',char(10)),'2026-04-07 22:12:01',2,'2026-04-07 22:12:01',2,NULL,NULL,0);
INSERT INTO basic_tests VALUES(60,'Do all USB ports work on the device?','USB Ports check',7,10,'Please check every USB port. Using a keyboard is the quick/easy test.','2026-04-07 22:13:45',2,'2026-04-07 22:13:45',2,NULL,NULL,0);
INSERT INTO basic_tests VALUES(61,'Can you upgrade from previous version to latest?','Version Upgrade',1,11,'Primary concern is kernel installs and boots after upgrade.','2026-04-07 22:14:23',2,'2026-04-07 22:14:23',2,NULL,NULL,0);
INSERT INTO basic_tests VALUES(62,'Torrents','Torrents',9,1,replace('Verify torrents are created and function\n\nDownload torrent file and verify that tracker is working and files download - preeseeding is also a useful test','\n',char(10)),'2026-04-07 22:15:58',2,'2026-04-07 22:15:58',2,NULL,NULL,0);
INSERT INTO basic_tests VALUES(63,'Apply Errata','Apply Errata',9,2,' Apply Errata','2026-04-07 22:16:31',2,'2026-04-07 22:16:31',2,NULL,NULL,0);
INSERT INTO basic_tests VALUES(64,'Mirror sync - post an update','Mirror Sync Post',9,3,'Post an update to the channel that the mirror sync has begun and we are approximately 36 hours from release. This gives everyone an estimated time to work from so that it isn''t a constant pestering to ~infrastructure .','2026-04-07 22:17:24',2,'2026-04-07 22:17:24',2,NULL,NULL,0);
INSERT INTO basic_tests VALUES(65,'Mirror sync','Mirror sync',9,4,'Make sure a few mirrors have a sync of the data','2026-04-07 22:18:01',2,'2026-04-07 22:18:01',2,NULL,NULL,0);
INSERT INTO basic_tests VALUES(66,'Check du listing','Check du listing',9,5,replace('Create a du listing of folder sizes for mirrors to check progress against\n\n*  `$ du -ch --max-depth=1 X.Y/`\n* `Post information in ~infrastructure `','\n',char(10)),'2026-04-07 22:19:24',2,'2026-04-07 22:19:24',2,NULL,NULL,0);
INSERT INTO basic_tests VALUES(67,'Give partners/relevant parties advance notice','Advance Notice',10,1,'Give partners / relevant parties advance notice','2026-04-07 22:21:30',2,'2026-04-07 22:21:30',2,NULL,NULL,0);
INSERT INTO basic_tests VALUES(68,' rockylinux.org Announcment','Announce: rockylinux.org',10,2,'Make announcement on rockylinux.org','2026-04-07 22:22:32',2,'2026-04-07 22:22:32',2,NULL,NULL,0);
INSERT INTO basic_tests VALUES(69,'Announcement: Bluesky','Announcement: Bluesky',10,3,'Make Announcement on Bluesky','2026-04-07 22:23:16',2,'2026-04-07 22:23:16',2,NULL,NULL,0);
INSERT INTO basic_tests VALUES(70,'Announcement: LinkedIn','Announcement: LinkedIn',10,4,'Make Announcement on Linked In','2026-04-07 22:23:56',2,'2026-04-07 22:23:56',2,NULL,NULL,0);
INSERT INTO basic_tests VALUES(71,'Announcement: Fediverse','Announcement: Fediverse',10,5,'Make Announcement on Fediverse','2026-04-07 22:24:34',2,'2026-04-07 22:24:34',2,NULL,NULL,0);
INSERT INTO basic_tests VALUES(72,' Publish Release Notes','Publish Release Notes',10,6,' Publish Release Notes','2026-04-07 22:25:06',2,'2026-04-07 22:25:06',2,NULL,NULL,0);
INSERT INTO basic_tests VALUES(73,'Bind','Bind',8,1,'Sparky test for BIND','2026-04-07 22:44:41',1,'2026-04-07 22:44:41',1,'https://git.resf.org/testing/Sparky_Bind',NULL,0);
INSERT INTO basic_tests VALUES(74,'Caddy','Caddy',8,2,'Sparky test for Caddy','2026-04-07 22:44:41',1,'2026-04-07 22:44:41',1,'https://git.resf.org/testing/Sparky_Caddy',NULL,0);
INSERT INTO basic_tests VALUES(75,'Knot','Knot',8,3,'Sparky test for Knot','2026-04-07 22:44:41',1,'2026-04-07 22:44:41',1,'https://git.resf.org/testing/Sparky_Knot',NULL,0);
INSERT INTO basic_tests VALUES(76,'Nginx Multi-Site','Nginx Multi-Site',8,4,'Sparky test for Nginx (Multi-Site)','2026-04-07 22:44:41',1,'2026-04-07 22:44:41',1,'https://git.resf.org/testing/Sparky_Nginx_Multi_Site',NULL,0);
INSERT INTO basic_tests VALUES(77,'Nginx Single-Site','Nginx Single-Site',8,5,'Sparky test for Nginx (Single-Site)','2026-04-07 22:44:41',1,'2026-04-07 22:44:41',1,'https://git.resf.org/testing/Sparky_Nginx_Single_Site',NULL,0);
INSERT INTO basic_tests VALUES(78,'NSD','NSD',8,6,'Sparky test for NSD','2026-04-07 22:44:41',1,'2026-04-07 22:44:41',1,'https://git.resf.org/testing/Sparky_NSD',NULL,0);
INSERT INTO basic_tests VALUES(79,'PHP','PHP',8,7,'Sparky test for PHP','2026-04-07 22:44:41',1,'2026-04-07 22:44:41',1,'https://git.resf.org/testing/Sparky_PHP',NULL,0);
INSERT INTO basic_tests VALUES(80,'Podman','Podman',8,8,'Sparky test for Podman','2026-04-07 22:44:41',1,'2026-04-07 22:44:41',1,'https://git.resf.org/testing/Sparky_Podman',NULL,0);
INSERT INTO basic_tests VALUES(81,'Python SSL','Python SSL',8,9,'Sparky test for Python SSL','2026-04-07 22:44:41',1,'2026-04-07 22:44:41',1,'https://git.resf.org/testing/Sparky-Python-SSL',NULL,0);
INSERT INTO basic_tests VALUES(82,'Redis','Redis',8,10,'Sparky test for Redis','2026-04-07 22:44:41',1,'2026-04-07 22:44:41',1,'https://git.resf.org/testing/Sparky-Redis',NULL,0);
INSERT INTO basic_tests VALUES(83,'Slurm','Slurm',8,11,'Sparky test for Slurm','2026-04-07 22:44:41',1,'2026-04-07 22:44:41',1,'https://git.resf.org/testing/Sparky_Slurm',NULL,0);
INSERT INTO basic_tests VALUES(84,'Swap(DNF)','Swap(DNF)',8,12,'Sparky test for Swap(DNF)','2026-04-07 22:44:41',1,'2026-04-07 22:44:41',1,'https://git.resf.org/testing/Sparky_Swap',NULL,0);
INSERT INTO basic_tests VALUES(85,'Unbound','Unbound',8,13,'Sparky test for Unbound','2026-04-07 22:44:41',1,'2026-04-07 22:44:41',1,'https://git.resf.org/testing/Sparky_Unbound',NULL,0);
INSERT INTO basic_tests VALUES(86,'WP Lamp','WP Lamp',8,14,'Sparky test for WP Lamp','2026-04-07 22:44:41',1,'2026-04-07 22:44:41',1,'https://git.resf.org/testing/Sparky_WP_Lamp',NULL,0);
INSERT INTO basic_tests VALUES(87,'ZFS-2.2.9','ZFS-2.2.9',8,15,'Sparky test for ZFS (v2.2.9)','2026-04-07 22:44:41',1,'2026-04-07 22:44:41',1,'https://git.resf.org/testing/Sparky_ZFS',NULL,0);
INSERT INTO basic_tests VALUES(88,'ZFS-2.3.5','ZFS-2.3.5',8,16,'Sparky test for ZFS (v2.3.5)','2026-04-07 22:44:41',1,'2026-04-07 22:44:41',1,'https://git.resf.org/testing/Sparky_ZFS',NULL,0);
CREATE TABLE test_types (
	id INTEGER NOT NULL, 
	basic_test_id INTEGER NOT NULL, 
	arch VARCHAR NOT NULL, 
	test_environ VARCHAR NOT NULL, 
	claimant_id INTEGER, 
	notes VARCHAR, 
	PRIMARY KEY (id), 
	FOREIGN KEY(basic_test_id) REFERENCES basic_tests (id), 
	FOREIGN KEY(claimant_id) REFERENCES users (id)
);
CREATE TABLE test_results (
	id INTEGER NOT NULL, 
	basic_tests_id INTEGER NOT NULL, 
	test_book VARCHAR NOT NULL, 
	user_id INTEGER NOT NULL, 
	arch VARCHAR NOT NULL, 
	deploy_type VARCHAR NOT NULL, 
	status VARCHAR NOT NULL, 
	submitted DATETIME NOT NULL, 
	comments VARCHAR, adminpass INTEGER default 0, rcname VARCHAR DEFAULT 'base', 
	PRIMARY KEY (id), 
	CONSTRAINT "uniqResults" UNIQUE (basic_tests_id, test_book, arch, deploy_type, user_id, submitted), 
	CONSTRAINT status_check CHECK (status IN ('pass', 'fail', 'partial')), 
	FOREIGN KEY(basic_tests_id) REFERENCES basic_tests (id), 
	FOREIGN KEY(user_id) REFERENCES users (id)
);
INSERT INTO test_results VALUES(1,6,'RockyLinux-10.1',2,'aarch64','Container','pass','2026-04-08 21:00:23','Adding Pass for test 6 -- aarch64/Container',0,'base');
INSERT INTO test_results VALUES(2,1,'RockyLinux-10.1',2,'x86_64','VM','fail','2026-04-08 21:48:57','',0,'base');
INSERT INTO test_results VALUES(3,1,'RockyLinux-10.1',2,'ppc64le','VM','fail','2026-04-08 21:55:40','up the fail count',0,'base');
INSERT INTO test_results VALUES(4,1,'RockyLinux-10.1',2,'ppc64le','Bare Metal','fail','2026-04-08 21:55:56','this one for bare metal',0,'base');
INSERT INTO test_results VALUES(5,1,'RockyLinux-10.1',2,'ppc64le','Container','fail','2026-04-08 21:56:11','and container',0,'base');
INSERT INTO test_results VALUES(6,1,'RockyLinux-10.1',2,'ppc64le','CloudVM','pass','2026-04-08 21:56:29','but a pass for cloud VM ??',0,'base');
INSERT INTO test_results VALUES(7,1,'RockyLinux-10.2',3,'x86_64','VM','pass','2026-04-11 02:43:28','Submitting a VM Pass for x86_64',0,'base');
INSERT INTO test_results VALUES(8,1,'RockyLinux-10.2',3,'x86_64','Container','partial','2026-04-11 02:43:53','Setting a Partial result for x86_64 on a container',0,'base');
INSERT INTO test_results VALUES(9,1,'RockyLinux-10.2',3,'x86_64','CloudVM','fail','2026-04-11 03:37:36','Failing on Cloud-VM -- too bad!',0,'base');
INSERT INTO test_results VALUES(10,1,'RockyLinux-10.2',3,'aarch64','VM','pass','2026-04-11 04:30:53',replace('Submitting a multiline Pass\nThat could be using markdown, I guess\n\n# With a title here','\n',char(10)),0,'base');
INSERT INTO test_results VALUES(11,1,'RockyLinux-10.2',5,'x86_64','VM','pass','2026-04-11 21:34:58','Attempting to set AdminPass on',0,'base');
INSERT INTO test_results VALUES(12,1,'RockyLinux-10.2',5,'x86_64','VM','pass','2026-04-11 21:36:50','trying again with adminpass',1,'base');
INSERT INTO test_results VALUES(13,2,'RockyLinux-10.2',5,'x86_64','VM','pass','2026-04-11 21:40:19','adminpass for mediacheck',1,'base');
INSERT INTO test_results VALUES(14,1,'RockyLinux-10.2',5,'x86_64','VM','partial','2026-04-11 21:55:52','',1,'base');
INSERT INTO test_results VALUES(15,1,'RockyLinux-10.2',5,'x86_64','VM','partial','2026-04-11 22:03:18','are there comments here',1,'base');
INSERT INTO test_results VALUES(16,1,'RockyLinux-10.2',5,'x86_64','VM','partial','2026-04-11 22:04:53','dumb comments',1,'base');
INSERT INTO test_results VALUES(17,4,'RockyLinux-10.2',5,'x86_64','VM','fail','2026-04-11 22:17:42','',0,'base');
INSERT INTO test_results VALUES(18,4,'RockyLinux-10.2',5,'x86_64','VM','fail','2026-04-11 22:17:48','',0,'base');
INSERT INTO test_results VALUES(19,4,'RockyLinux-10.2',5,'x86_64','VM','fail','2026-04-11 22:17:53','',0,'base');
INSERT INTO test_results VALUES(20,8,'RockyLinux-10.2',5,'x86_64','CloudVM','partial','2026-04-11 23:01:16','',1,'base');
INSERT INTO test_results VALUES(21,13,'RockyLinux-10.2',5,'x86_64','VM','fail','2026-04-11 23:16:11','',1,'base');
INSERT INTO test_results VALUES(22,1,'RockyLinux-10.2',5,'x86_64','VM','pass','2026-04-13 22:01:54','',0,'RC1');
CREATE INDEX ix_users_username ON users (username);
CREATE INDEX ix_test_books_name ON test_books (name);
CREATE INDEX ix_basic_tests_shortname ON basic_tests (shortname);
CREATE INDEX ix_basic_tests_name ON basic_tests (name);
CREATE INDEX ix_test_results_submitted ON test_results (submitted);
CREATE INDEX ix_test_results_basic_tests_id ON test_results (basic_tests_id);
CREATE INDEX ix_test_results_test_book ON test_results (test_book);
CREATE INDEX ix_test_results_user_id ON test_results (user_id);
CREATE INDEX ix_test_results_status ON test_results (status);
CREATE INDEX ix_test_results_arch ON test_results (arch);
COMMIT;
