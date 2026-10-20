"""Replace the rebuilt native module; preserve Boot's stored nested-JAR format."""
from pathlib import Path
import sys
import zipfile

original, core, output = map(Path, sys.argv[1:])
entry = 'BOOT-INF/lib/certify-core-1.0.0-alpha.1.jar'
with zipfile.ZipFile(core) as library:
    assert library.testzip() is None
    assert 'io/mosip/certify/core/dto/CredentialRequest.class' in library.namelist()
with zipfile.ZipFile(original) as source, zipfile.ZipFile(output, 'w') as target:
    assert source.namelist().count(entry) == 1, 'Pinned upstream native module was not found'
    for info in source.infolist():
        data = core.read_bytes() if info.filename == entry else source.read(info.filename)
        if info.filename == entry:
            info.compress_type = zipfile.ZIP_STORED
        target.writestr(info, data)
with zipfile.ZipFile(output) as built:
    assert built.testzip() is None
    assert built.getinfo(entry).compress_type == zipfile.ZIP_STORED
