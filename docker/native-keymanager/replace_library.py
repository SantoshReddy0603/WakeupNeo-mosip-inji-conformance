"""Install the rebuilt native library, preserving Spring Boot's ZIP requirements."""
from pathlib import Path
import zipfile

ENTRY = 'BOOT-INF/lib/kernel-keymanager-service-1.4.0-lib.jar'
CLASS = 'io/mosip/kernel/keymanager/hsm/util/CertificateUtility.class'

def replace(original, library, output):
    original, library, output = map(Path, [original, library, output])
    with zipfile.ZipFile(library) as jar:
        assert jar.testzip() is None
        assert CLASS in jar.namelist()
        assert b'generateSerialNumber' in jar.read(CLASS)
    with zipfile.ZipFile(original) as source, zipfile.ZipFile(output, 'w') as destination:
        assert source.namelist().count(ENTRY) == 1
        for info in source.infolist():
            data = library.read_bytes() if info.filename == ENTRY else source.read(info.filename)
            if info.filename == ENTRY:
                info.compress_type = zipfile.ZIP_STORED
            destination.writestr(info, data)
    with zipfile.ZipFile(output) as final:
        assert final.testzip() is None
        assert final.read(ENTRY) == library.read_bytes()

if __name__ == '__main__':
    import sys
    replace(*sys.argv[1:])
