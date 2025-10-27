import nbtlib, gzip, io


def load_nbt(path):
    try:
        nbt_file = nbtlib.load(path)
        return nbt_file, nbt_file.root_name, nbt_file
    except Exception:
        with gzip.open(path, "rb") as g:
            bio = io.BytesIO(g.read())
        nbt_file = nbtlib.File.parse(bio)
        return nbt_file, nbt_file.root_name, nbt_file


def save_nbt_file(nbt_file, path=None):
    nbt_file.save(path or getattr(nbt_file, 'filename', None))


def coerce_to_tag(cur, new):
    # Converts string input to the same type as current NBT tag
    if isinstance(cur, nbtlib.tag.Byte): return nbtlib.tag.Byte(int(new))
    if isinstance(cur, nbtlib.tag.Short): return nbtlib.tag.Short(int(new))
    if isinstance(cur, nbtlib.tag.Int): return nbtlib.tag.Int(int(new))
    if isinstance(cur, nbtlib.tag.Long): return nbtlib.tag.Long(int(new))
    if isinstance(cur, nbtlib.tag.Float): return nbtlib.tag.Float(float(new))
    if isinstance(cur, nbtlib.tag.Double): return nbtlib.tag.Double(float(new))
    if isinstance(cur, nbtlib.tag.String): return nbtlib.tag.String(new)
    if isinstance(cur, nbtlib.tag.ByteArray): return nbtlib.tag.ByteArray([int(x.strip()) for x in new.split(',')])
    if isinstance(cur, nbtlib.tag.IntArray): return nbtlib.tag.IntArray([int(x.strip()) for x in new.split(',')])
    if isinstance(cur, nbtlib.tag.LongArray): return nbtlib.tag.LongArray([int(x.strip()) for x in new.split(',')])
    try:
        return nbtlib.tag.Int(int(new))
    except:
        return nbtlib.tag.String(new)


def build_tag_from_inputs(typ, val):
    typ = typ.lower()
    import nbtlib
    if typ == 'byte': return nbtlib.tag.Byte(int(val))
    if typ == 'short': return nbtlib.tag.Short(int(val))
    if typ == 'int': return nbtlib.tag.Int(int(val))
    if typ == 'long': return nbtlib.tag.Long(int(val))
    if typ == 'float': return nbtlib.tag.Float(float(val))
    if typ == 'double': return nbtlib.tag.Double(float(val))
    if typ == 'string': return nbtlib.tag.String(val or '')
    if typ == 'compound': return nbtlib.tag.Compound()
    if typ == 'list': return nbtlib.tag.List()
    if typ == 'bytearray': return nbtlib.tag.ByteArray([int(x.strip()) for x in (val or '').split(',') if x.strip()])
    if typ == 'intarray': return nbtlib.tag.IntArray([int(x.strip()) for x in (val or '').split(',') if x.strip()])
    if typ == 'longarray': return nbtlib.tag.LongArray([int(x.strip()) for x in (val or '').split(',') if x.strip()])
    raise ValueError(f'Unknown type {typ}')
