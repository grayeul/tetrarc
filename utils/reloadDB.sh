#!/bin/bash
# reloadDB.sh
# This reloads the database from scratch
#
read -p "Are you sure you want to remove/recreate the DB? (yes|NO)" ans

if [ "$ans" != "yes" ];then
	echo "Answer not confirmed, aborting"
	exit
fi

rm -f tetrarc.db
python -m tetrarc.utils.tdb -load data/books.csv
python -m tetrarc.utils.tdb -load data/test_groups.csv
python -m tetrarc.utils.tdb -load data/UserList.csv
python -m tetrarc.utils.tdb -load data/RolesList.csv

# Add standard users:
cat << EOF | sqlite3 tetrarc.db
INSERT INTO users VALUES(2,'rocky','rocky','bob@rockylinux.org','2026-03-24 16:28:28',0,X'24326224313524513776734d674246666672752f314f4966364f6d4875795846396750305767773774577841314d386a704d744d6a7a686e2e57694b',NULL,0);

EOF
# Now setup default roles
# rocky is admin
cat << EOF | sqlite3 tetrarc.db
insert into user_roles (user_id,role_id) values (2,1);
EOF

