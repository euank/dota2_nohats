from binary import Struct, Magic, Format, Offset, Seek, Array, FixedString, String
import json

class MDL(Struct):
    def fields(self):
        self.F("magic", Magic("IDST"))
        self.F("version", Format("I"))
        self.F("checksum", Format("I"))
        self.F("name", FixedString(64))
        self.F("datalength", Format("I"))

        self.F("eyepos", Format("3f"))
        self.F("illum", Format("3f"))
        self.F("hull_min", Format("3f"))
        self.F("hull_max", Format("3f"))
        self.F("view_bbmin", Format("3f"))
        self.F("view_bbmax", Format("3f"))

        self.F("flags", Format("I"))

        self.F("bone", Format("II"))
        self.F("bonecontroller", Format("II"))
        self.F("hitbox", Format("II"))

        self.F("numlocalanim", Format("I"))
        self.F("localanimoffset", Format("I"))

        self.F("numlocalsequence", Format("I"))
        self.F("localsequenceoffset", Format("I"))

        self.F("texture", Format("II"))
        self.F("cdtexture", Format("II"))

        self.F("unknown", Format("II"))

        self.F("numskinref", Format("I"))
        self.F("numskinfamilies", Format("I"))
        self.F("skinindex", Format("I"))

        self.F("bodypart", Format("II"))
        self.F("localattachment", Format("II"))

        self.F("numlocalnodes", Format("I"))
        self.F("localnodeindex", Format("I"))
        self.F("localnodenameindex", Format("I"))

        # rest broken due to unkown fields added

        with Seek(s, self.field["localanimoffset"].data):
            self.F("localanim", Array(self.field["numlocalanim"].data, LocalAnim))
        with Seek(s, self.field["localsequenceoffset"].data):
            self.F("localsequence", Array(self.field["numlocalsequence"].data, LocalSequence))

        return

        self.F("flexdesc", Format("II"))
        self.F("flexcontroller", Format("II"))
        self.F("flexrule", Format("II"))
        self.F("ikchain", Format("II"))
        self.F("mouth", Format("II"))

        self.F("keyvalueindex", Format("I"))
        self.F("keyvaluesize", Format("I"))

        self.F("localikautoplaylock", Format("II"))

        self.F("mass", Format("f"))
        self.F("contents", Format("I"))

        self.F("includemodels", Format("II"))

        self.F("bonetablebynameindex", Format("I"))
        self.F("vertexbase", Format("I"))
        self.F("indexbase", Format("I"))
        self.F("constdirectionallightdot", Format("B"))
        self.F("rootLOD", Format("B"))
        self.F("numAllowedRootLODs", Format("B"))
        self.F("unused", Format("B"))
        self.F("unused4", Format("I"))

        self.F("flexcontrollerui", Format("II"))

        self.F("unused3", Format("2I"))
        self.F("studiohdr2index", Format("I"))
        self.F("unused2", Format("1I"))

class BasePointer(Format):
    def __init__(self, fmt):
        Format.__init__(self, fmt)

    def _unpack(self, s):
        this = s.tell()
        data = Format._unpack(self, s)
        assert data == -this
        return data

    def _pack(self, s, data):
        this = s.tell()
        Format._pack(self, s, self.data)

class Relative(Format):
    def __init__(self, field, fmt):
        self.field = field
        Format.__init__(self, fmt)

    def _unpack(self, s):
        data = Format._unpack(self, s)
        if data != 0:
            data += self.field.data
        return data

    def _pack(self, s, data):
        if data != 0:
            data += self.field.packed_at
        Format._pack(self, s, data)

class RelativeString(Relative):
    def _unpack(self, s):
        data = Relative._unpack(self, s)
        with Seek(s, data):
            string = String()._unpack(s)
        return [data, string]

    def _pack(self, s, data):
        data = data[0]
        Relative._pack(self, s, data)

class LocalAnim(Struct):
    def fields(self):
        base = self.F("base", Offset())
        self.F("baseptr", BasePointer("i"))
        self.F("nameindex", RelativeString(base, "i"))
        self.F("fps", Format("f"))
        self.F("flags", Format("I"))
        self.F("numframes", Format("I"))
        self.F("nummovements", Format("I"))
        self.F("movementindex", Relative(base, "i"))
        self.F("unused", Format("6I"))
        self.F("animblock", Format("i"))
        self.F("animindex", Relative(base, "i"))
        self.F("numikrules", Format("I"))
        self.F("ikruleindex",Relative(base, "i"))
        self.F("animblockikruleindex", Relative(base, "i"))
        self.F("numlocalhierarchy", Format("I"))
        self.F("localhierarchyindex", Relative(base, "i"))
        self.F("sectionindex", Relative(base, "i"))
        self.F("sectionframes", Format("I"))
        self.F("zeroframespan", Format("h"))
        self.F("zeroframecount", Format("h"))
        self.F("zeroframeindex", Relative(base, "i"))
        self.F("zeroframestalltime", Format("f"))

class LocalSequence(Struct):
    def fields(self):
        base = self.F("base", Offset())
        self.F("baseptr", BasePointer("i"))
        self.F("labelindex", RelativeString(base, "i"))
        self.F("activitynameindex", RelativeString(base, "i"))
        self.F("flags", Format("I"))
        self.F("activity", Format("i"))
        self.F("actweight", Format("I"))
        self.F("numevents", Format("I"))
        self.F("eventindex", Relative(base, "i"))
        self.F("bbmin", Format("3f"))
        self.F("bbmax", Format("3f"))
        self.F("numblends", Format("I"))
        self.F("animindex", Relative(base, "i"))
        self.F("movementindex", Relative(base, "i"))
        self.F("groupsize", Format("2I"))
        self.F("paramindex", Format("2i"))
        self.F("paramstart", Format("2f"))
        self.F("paramend", Format("2f"))
        self.F("paremparent", Format("I"))
        self.F("fadeintime", Format("f"))
        self.F("fadeouttime", Format("f"))
        self.F("localentrynode", Format("I"))
        self.F("localexitnode", Format("I"))
        self.F("nodeflags", Format("I"))
        self.F("entryphase", Format("f"))
        self.F("exitphase", Format("f"))
        self.F("lastframe", Format("f"))
        self.F("nextseg", Format("I"))
        self.F("pose", Format("I"))
        self.F("numikrules", Format("I"))
        self.F("numautolayers", Format("I"))
        self.F("autolayerindex", Relative(base, "i"))
        self.F("weightlistindex", Relative(base, "i"))
        self.F("posekeyindex", Relative(base, "i"))
        self.F("numiklocks", Format("I"))
        self.F("iklockindex", Format("I"))
        self.F("keyvalueindex", Relative(base, "i"))
        self.F("keyvaluesize", Format("I"))
        self.F("cycleposeindex", Relative(base, "i"))
        self.F("overrideindex", Relative(base, "i"))
        self.F("numoverride", Format("I"))
        self.F("unused", Format("5I"))

        #with Seek(s, self.field["eventindex"].data):
        #    self.F("event", Array(self.field["numevents"].data, Event))
        with Seek(s, self.field["overrideindex"].data):
            self.F("override", Array(self.field["numoverride"].data, Override))

class Override(Struct):
    def fields(self):
        base = self.F("base", Offset())
        self.F("szindex", RelativeString(base, "i"))

class Event(Struct):
    def fields(self):
        base = self.F("base", Offset())
        self.F("cycle", Format("f"))
        self.F("event", Format("I"))
        self.F("type", Format("I"))
        self.F("options", FixedString(64))
        self.F("szeventindex", RelativeString(base, "i"))

with open("windrunner.mdl", "rb") as s:
    m = MDL()
    m.unpack(s)
    sequences = m.field["localsequence"].field
    for i in xrange(len(sequences)):
        sequence = sequences[i].data
        print "sequence", i
        print "--", sequence["labelindex"][1]
        print "--", sequence["activitynameindex"][1]
        print "--", [override["szindex"][1] for override in sequence["override"]]

    print json.dumps(m.data, indent=4)
    exit(0)

with open("windrunner.mdl", "rb") as s:
    with Seek(s, localseq_offset):
        for i in xrange(localseq_count):
            this = s.tell()
            baseptr, labelindex, activitynameindex, flags = getunpack(s, "<iiiI")
            assert baseptr == -this

            activity, actweight, numevents, eventindex = getunpack(s, "<iIIi")
            bbmin = getunpack(s, "<3f")
            bbmax = getunpack(s, "<3f")

            numblends, animindex, movementindex = getunpack(s, "<Iii")
            groupsize = getunpack(s, "<2I")
            paramindex = getunpack(s, "<2I")
            paramstart = getunpack(s, "<2f")
            paramend = getunpack(s, "<2f")
            paramparent = getunpack(s, "<I")

            fadeintime, fadeouttime = getunpack(s, "<ff")
            localentrynode, localexitnode, nodeflags = getunpack(s, "<III")
            entryphase, exitphase, lastframe, nextseq, pose = getunpack(s, "<fffII")
            numikrules, numautolayers, autolayerindex, weightlistindex = getunpack(s, "<IIii")
            posekeyindex, numiklocks, iklockindex = getunpack(s, "<iIi")
            keyvalueindex, keyvaluesize, cycleposeindex = getunpack(s, "<iIi")

            unused = getunpack(s, "<7i")

            with Seek(s, this + labelindex):
                label = getstring(s, '\0')

            with Seek(s, this + activitynameindex):
                activityname = getstring(s, '\0')

            print "label =", label, "+ activity =", activityname