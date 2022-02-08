# CNM25 2M DRC deck

# Initialise DRC package. 
from ui import *
cv = ui().getEditCellView()
geomBegin(cv)

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
pad       = geomGetShapes("CAPS", "drawing")

# Form derived layers
gate        = geomAnd(polygate, active)
ngate       = geomAnd(gate, nimp)
pgate       = geomAndNot(gate, ngate)
cpoly       = geomAnd(polygate, polycap)
polygatecont= geomAnd(polygate, cont)
polycapcont = geomAnd(polycap, cont)
activecont  = geomAnd(active, cont)
allcon      = geomOr(geomOr(polygatecont, polycapcont),activecont)
badcon      = geomAndNot(allcon, metal1)
metal1via   = geomAnd(metal1, via12)
badvia      = geomAndNot(metal1via, metal2)
diff        = geomAndNot(active, gate)
ndiff       = geomAnd(diff, nimp)
pdiff       = geomAndNot(diff, nimp)
ntap        = geomAnd(ndiff, nwell)
ptap        = geomAndNot(pdiff, nwell)

# Form connectivity
geomConnect( [
              [ntap, nwell, ndiff],
			  [cont, ndiff, metal1],
			  [cont, pdiff, metal1],
			  [cont, polygate, metal1],
			  [cont, polycap, metal1],
              [via12, metal1, metal2]
	     ] )

# Start design rule checking

# Checking off-grid...
print("0.0. Checking off-grid...")
geomOffGrid(nwell, 0.25, 1.0, "Error: N-well grid not multiple of 0.25um x 0.25um")
geomOffGrid(active, 0.25, 1.0, "Error: GASAD grid not multiple of 0.25um x 0.25um")
geomOffGrid(polygate, 0.25, 1.0, "Error: Poly1 grid not multiple of 0.25um x 0.25um")
geomOffGrid(polycap, 0.25, 1.0, "Error: Poly0 grid not multiple of 0.25um x 0.25um")
geomOffGrid(nimp, 0.25, 1.0, "Error: N-plus grid not multiple of 0.25um x 0.25um")
geomOffGrid(cont, 0.25, 1.0, "Error: Contact grid not multiple of 0.25um x 0.25um")
geomOffGrid(metal1, 0.25, 1.0, "Error: Metal1 grid not multiple of 0.25um x 0.25um")
geomOffGrid(via12, 0.25, 1.0, "Error: Via grid not multiple of 0.25um x 0.25um")
geomOffGrid(metal2, 0.25, 1.0, "Error: Metal2 grid not multiple of 0.25um x 0.25um")
geomOffGrid(pad, 0.25, 1.0, "Error: Pad grid not multiple of 0.25um x 0.25um")

# Checking N-well..
print("1.X. Checking N-well...")
geomWidth(nwell, 8.0, "Error: N-well width < 8um (see rule 1.1)")
geomSpace(nwell, 8.0, "Error: N-well spacing < 8um (see rule 1.2)")
geomNotch(nwell, 8.0, "Error: N-well notch < 8um (see rule 1.2)")

# Checking GASAD...
print("2.X. Checking GASAD...")
geomWidth(active, 2.0, "Error: GASAD width < 2um (see rule 2.1)")
geomSpace(active, 4.0, "Error: GASAD spacing < 4um (see rule 2.2)")
geomNotch(active, 4.0, "Error: GASAD notch < 4um (see rule 2.2)")
geomEnclose(nwell, pdiff, 5.0, "Error: N-well enclosure of P-plus active < 5um (see rule 2.3)")
geomSpace(nwell, ndiff, 5.0, "Error: N-well spacing to N-plus active < 5um (see rule 2.4)")

# Checking Poly0...
print("3.X. Checking Poly0...")
geomWidth(polycap, 2.5, "Error: Poly0 width < 2.5um (see rule 3.1)")
geomSpace(polycap, 6.0, "Error: Poly0 spacing < 6um (see rule 3.2)")
geomNotch(polycap, 6.0, "Error: Poly0 notch < 6um (see rule 3.2)")
geomSpace(polycap, active, 6.0, "Error: Poly0 spacing to GASAD < 6um (see rule 3.3)")

# Checking Poly1...
print("4.X. Checking Poly1...")
geomWidth(gate, 3.0, "Error: Poly1 width inside GASAD < 3um (see rule 4.1.a)")
geomWidth(geomAndNot(polygate, gate), 2.5, "Error: Poly1 width outside GASAD < 2.5um (see rule 4.1.b)")
geomSpace(polygate, 3.0, "Error: Poly1 spacing < 3um (see rule 4.2)")
geomNotch(polygate, 3.0, "Error: Poly1 notch < 3um (see rule 4.2)")
geomExtension(active, polygate, 3.0 , "Error: GASAD extension of Poly1 < 3um (see rule 4.3)")
geomExtension(polygate, active, 2.5, "Error: Poly1 extension of GASAD < 2.5um (see rule 4.4)")
geomSpace(polygate, active, 1.25, "Error: Poly1 spacing to GASAD < 1.25um (see rule 4.5)")
geomEnclose(polycap, polygate, 3.0, "Error: Poly0 enclosure of Poly1 < 3um (see rule 4.6)")

# Checking N-plus...
print("5.X. Checking N-plus...")
geomEnclose(nimp, active, 2.5, "Error: N-plus enclosure of GASAD < 2.5um (see rule 5.1)")
geomSpace(nimp, pdiff, 2.5, "Error: N-plus spacing to P-plus active < 2.5um (see rule 5.2)")
geomSpace(nimp, pgate, 2.0, "Error: N-plus spacing to Poly1 inside P-plus active < 2um (see rule 5.3)")
geomExtension(nimp, ngate, 1.5, "Error: N-plus extension of Poly1 inside N-plus active < 1.5um (see rule 5.4)")
geomWidth(nimp, 2.5, "Error: N-plus width < 2.5um (see rule 5.5)")
geomSpace(nimp, 2.5, "Error: N-plus spacing < 2.5um (see rule 5.6)")
geomNotch(nimp, 2.5, "Error: N-plus notch < 2.5um (see rule 5.6)")

# Checking Contact...
print("6.X. Checking Contact...")
saveDerived(badcon, "Error: Contact without Metal1")
geomWidth(cont, 2.5, not_equal, "Error: Contact size not equal to 2.5um x 2.5um (see rule 6.1)")
geomSpace(cont, 3.0, "Error: Contact spacing < 3um (see rule 6.2)")
geomNotch(cont, 3.0, "Error: Contact notch < 3um (see rule 6.2)")
geomEnclose(active, cont, 1.0, "Error: GASAD enclosure of Contact < 1um (see rule 6.3)")
geomEnclose(polygate, cont, 1.25, "Error: Poly1 enclosure of Contact < 1.25um (see rule 6.4)")
geomSpace(polygatecont, 2.5, "Error: Poly1 Contact spacing to GASAD < 2.5um (see rule 6.5)")
geomSpace(cont, gate, 2.0, "Error: Contact spacing to Poly1 inside GASAD < 2um (see rule 6.6)")
# 6.7 and 6.8 not implemented!
geomEnclose(polycap, cont, 4.0, "Error: Poly0 enclosure of Contact < 4um (see rule 6.9)")
geomSpace(cont, cpoly, 4.0, "Error: Contact spacing to Poly1 & Poly0 < 4um (see rule 6.10)")

# Checking Metal1...
print("7.X. Checking Metal1...")
geomWidth(metal1, 2.5, "Error: Metal1 width < 2.5um (see rule 7.1)")
geomSpace(metal1, 3.0, "Error: Metal1 spacing < 3um (see rule 7.2)")
geomNotch(metal1, 3.0, "Error: Metal1 notch < 3um (see rule 7.2)")
geomEnclose(metal1, cont, 1.25, "Error: Metal1 enclosure of Contact < 1.25um (see rule 7.3)")

# Checking Via...
print("8.X. Checking Via...")
saveDerived(badvia, "Error: Via without Metal2")
geomWidth(via12, 3.0, not_equal, "Error: Via size not equal to 3um x 3um (see rule 8.1)")
geomSpace(via12, 3.5, "Error: Via spacing < 3.5um (see rule 8.2)")
geomNotch(via12, 3.5, "Error: Via notch < 3.5um (see rule 8.2)")
geomEnclose(metal1, via12, 1.25, "Error: Metal1 enclosure of Via < 1.25um (see rule 8.3)")
geomSpace(via12, cont, 2.5, "Error: Via spacing to contact < 2.5um (see rule 8.4)")
geomSpace(via12, polygate, 2.5, "Error: Via spacing to Poly1 < 2.5um (see rule 8.5)")

# Checking Metal2...
print("9.X. Checking Metal2...")
geomWidth(metal2, 3.5, "Error: Metal2 width < 3.5um (see rule 9.1)")
geomSpace(metal2, 3.5, "Error: Metal2 spacing < 3.5um (see rule 9.2)")
geomNotch(metal2, 3.5, "Error: Metal2 notch < 3.5um (see rule 9.2)")
geomEnclose(metal2, via12, 1.25, "Error: Metal2 enclosure of Via < 1.25um (see rule 9.3)")

# Checking Pad...
print("10.X. Checking Pad...")
geomWidth(pad, 100.0, not_equal, "Error: Pad size not equal to 100um x 100um (see rule 10.1)")

num_err = geomGetTotalCount()
print("** Total error count = ", num_err)

# Exit DRC package, freeing memory
geomEnd()

ui().winRedraw()

