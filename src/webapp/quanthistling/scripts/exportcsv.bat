set QUANTHISTLINGPATH=c:\Users\pbouda\Projects\svn-googlecode\qlc\src\webapp\quanthistling
set PATH=%PATH%;c:\Program Files (x86)\PostgreSQL\8.4\bin
call psql -U postgres -c "copy (select * from entry) to STDOUT DELIMITER AS E'\t' CSV HEADER;" quanthistling > %QUANTHISTLINGPATH%\tmp\csv\entry.csv
call psql -U postgres -c "copy (select * from annotation) to STDOUT DELIMITER AS E'\t' CSV HEADER;" quanthistling > %QUANTHISTLINGPATH%\tmp\csv\annotation.csv
call psql -U postgres -c "copy (select * from dictdata) to STDOUT DELIMITER AS E'\t' CSV HEADER;" quanthistling > %QUANTHISTLINGPATH%\tmp\csv\dictdata.csv
call psql -U postgres -c "copy (select * from nondictdata) to STDOUT DELIMITER AS E'\t' CSV HEADER;" quanthistling > %QUANTHISTLINGPATH%\tmp\csv\nondictdata.csv
call psql -U postgres -c "copy (select * from book) to STDOUT DELIMITER AS E'\t' CSV HEADER;" quanthistling > %QUANTHISTLINGPATH%\tmp\csv\book.csv
call psql -U postgres -c "copy (select * from language) to STDOUT DELIMITER AS E'\t' CSV HEADER;" quanthistling > %QUANTHISTLINGPATH%\tmp\csv\language.csv
call psql -U postgres -c "copy (select * from component) to STDOUT DELIMITER AS E'\t' CSV HEADER;" quanthistling > %QUANTHISTLINGPATH%\tmp\csv\component.csv
call psql -U postgres -c "copy (select * from corpusversion) to STDOUT DELIMITER AS E'\t' CSV HEADER;" quanthistling > %QUANTHISTLINGPATH%\tmp\csv\corpusversion.csv
call psql -U postgres -c "copy (select * from wordlist_entry) to STDOUT DELIMITER AS E'\t' CSV HEADER;" quanthistling > %QUANTHISTLINGPATH%\tmp\csv\wordlistentry.csv
call psql -U postgres -c "copy (select * from wordlist_annotation) to STDOUT DELIMITER AS E'\t' CSV HEADER;" quanthistling > %QUANTHISTLINGPATH%\tmp\csv\wordlistannotation.csv
call psql -U postgres -c "copy (select * from wordlistdata) to STDOUT DELIMITER AS E'\t' CSV HEADER;" quanthistling > %QUANTHISTLINGPATH%\tmp\csv\wordlistdata.csv
call psql -U postgres -c "copy (select * from wordlist_concept) to STDOUT DELIMITER AS E'\t' CSV HEADER;" quanthistling > %QUANTHISTLINGPATH%\tmp\csv\wordlistconcept.csv
