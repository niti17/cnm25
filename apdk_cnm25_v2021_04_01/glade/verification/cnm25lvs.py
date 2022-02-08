# CNM25 2M extraction deck

# Initialise boolean package. 
from ui import *
ui = cvar.uiptr
cv = ui.getEditCellView()
geomBegin(cv)
libxtrlvs = cv.lib()

# Get raw layers
nwell     = geomGetShapes("NTUB", "drawing")
active    = geomGetShapes("GASAD", "drawing")
polygate  = geomGetShapes("POLY1", "drawing")
polycap   = geomGetShapes("POLY0", "drawing")
nimp      = geomGetShapes("NPLUS", "drawing")
cont      = geomGetShapes("WINDOW", "drawing")
metal1    = geomGetShapes("METAL", "drawing")
via12     = geomGetShapes("VIA", "drawing")
metal2    = geomGetShapes("METAL2", "drawing")

# Form derived layers
bkgnd       = geomBkgnd()
pwell       = geomAndNot(bkgnd, nwell)
gate        = geomAnd(polygate, active)
ngate       = geomAnd(gate, nimp)
pgate       = geomAndNot(gate, ngate)
cpoly       = geomAnd(polygate, polycap)
diff        = geomAndNot(active, gate)
ndiff       = geomAnd(diff, nimp)
pdiff       = geomAndNot(diff, nimp)
ntap        = geomAnd(ndiff, nwell)
ptap        = geomAnd(pdiff, pwell)

# Extract pin and net names before geomConnect
geomLabel(polygate, "POLY1", "pin", True)
geomLabel(metal1, "METAL", "pin", True)
geomLabel(metal2, "METAL2", "pin", True)
geomLabel(polygate, "POLY1", "net", False)
geomLabel(metal1, "METAL", "net", False)
geomLabel(metal2, "METAL2", "net", False)

# Form connectivity
geomConnect( [
        [pwell, bkgnd, pwell],
		[ptap, pwell, pdiff],
		[ntap, nwell, ndiff],
		[cont, ndiff, pdiff, polygate, polycap, metal1],
		[via12, metal1, metal2]
		] )

# Save interconnect
saveInterconnect( [
		[pwell, "PWELL"],
		nwell,
		[ptap, "GASAD"],
		[ntap, "GASAD"],
		[ndiff, "GASAD"],
		[pdiff, "GASAD"],
		polycap,
		polygate,
		cont,
		metal1,
		via12,
		metal2,
		] )

# Extracting devices
if geomNumShapes(ngate) > 0 :
	print("# Extracting NMOS transistors...")
	extractMOS("cnm25modn", ngate, polygate, ndiff, pwell)

if geomNumShapes(pgate) > 0 :
	print("# Extracting PMOS transistors...")
	extractMOS("cnm25modp", pgate, polygate, pdiff, nwell)

if geomNumShapes(cpoly) > 0 :
	print("# Extract PiP capacitors...")
	extractDevice("cnm25cpoly", cpoly, [[polygate, "T"], [polycap, "B"]])

print("# End of circuit extraction")
geomEnd()

# Reporting results
cv_ex = libxtrlvs.dbFindCellViewByName(cv.cellName(), "extracted")
box = cv_ex.bBox()
objs = cv_ex.dbGetOverlaps(box, 0, True, True, True)
obj = objs.first()
num_dev = 0
while obj :
	if obj.isInst() :
		num_dev = num_dev + 1
	obj = objs.next()
print("** Total device count = ", num_dev)

