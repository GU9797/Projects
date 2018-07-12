import CoolProp
import CoolProp.CoolProp as CP
import csv

def RefrigCalc(Refrig, ton, TIE, TOE, ApprEvap, SupHeat, TIC, TOC, ApprCond, Subcool, dH1_dH2, Eff1, Eff2, EffMotor, BearLoss):

    TCondOut = TOC + ApprCond
    TEvapOut = TOE - ApprEvap
    TEconOut = (TEvapOut + TCondOut) / 2

    #Evaporator
    PEvapOut = CP.PropsSI('P', 'T', TEvapOut, 'Q', 1, Refrig)
    HEvapOutVap = CP.PropsSI('H', 'P', PEvapOut, 'Q', 1, Refrig)
    HEvapOutLiq = CP.PropsSI('H', 'P', PEvapOut, 'Q', 0, Refrig)

    #Condenser
    PCondOut = CP.PropsSI('P', 'T', TCondOut, 'Q', 1, Refrig)
    HCondOutVap = CP.PropsSI('H', 'P', PCondOut, 'Q', 1, Refrig)
    HCondOutLiq = CP.PropsSI('H', 'P', PCondOut, 'Q', 0, Refrig)
    HCondOutCooled = CP.PropsSI('H', 'T', TCondOut - Subcool, 'Q', 0, Refrig)

    UpperBound = TCondOut
    LowerBound = TEvapOut
    #Economizer
    while True:
        PEconOut = CP.PropsSI('P', 'T', TEconOut, 'Q', 1, Refrig)
        HEconOutVap = CP.PropsSI('H', 'P', PEconOut, 'Q', 1, Refrig)
        HEconOutLiq = CP.PropsSI('H', 'P', PEconOut, 'Q', 0, Refrig)
        FlowRate1 = ton / (HEvapOutVap - HEconOutLiq)
        EconEff = (HCondOutCooled - HEconOutLiq) / (HEconOutVap - HEconOutLiq)
        GasFlow = (EconEff)/(1-EconEff)*FlowRate1
        FlowRate2 = FlowRate1 + GasFlow

        #Stage 1
        H1 = CP.PropsSI('H', 'P', PEvapOut, 'T', TEvapOut + SupHeat, Refrig)
        S1 = CP.PropsSI('S', 'P', PEvapOut, 'T', TEvapOut + SupHeat, Refrig)
        H2s = CP.PropsSI('H', 'P', PEconOut, 'S', S1, Refrig)
        H2 = H1 + (H2s - H1) / Eff1
        Power1 = FlowRate1*(H2 - H1)

        #Stage 2
        H21 = (FlowRate1*H2+GasFlow*HEconOutVap)/FlowRate2
        T21 = CP.PropsSI('T', 'P', PEconOut, 'H', H21, Refrig)
        S21 = CP.PropsSI('S', 'P', PEconOut, 'T', T21, Refrig)
        H22s = CP.PropsSI('H', 'P', PCondOut, 'S', S21, Refrig)
        H22 = H21 + (H22s - H21) / Eff2
        Power2 = FlowRate2*(H22 - H21)

        HRatio = (H2 - H1) / (H22 - H21)

        if HRatio - dH1_dH2 > .001:
            UpperBound = TEconOut
            TEconOut = (TEconOut - LowerBound) / 2 + LowerBound
        elif HRatio - dH1_dH2 < -.001:
            LowerBound = TEconOut
            TEconOut = (UpperBound - TEconOut) / 2 + TEconOut
        else:
            break

    PowerIn = BearLoss + (Power1 + Power2)/EffMotor
    COPCool = ton / PowerIn
    COPHeat = (PowerIn + ton)/(PowerIn)

    outfile = open('output.csv', 'w')
    outfile.write("\n")
    outfile.write("COP Cooling is " + str(COPCool) + "\n")
    outfile.write("COP Heating is " + str(COPHeat) + "\n")
    outfile.write("Power in is " + str(PowerIn) + " W" + "\n")
    outfile.write("\n")
    outfile.write("\n")
    outfile.write("STAGE 1" + "\n")
    outfile.write("FlowRate: " + str(FlowRate1)  + " kg/s" + "\n")
    outfile.write("Pressure at Evaporator: " + str(PEvapOut)  + " Pa" + "\n")
    outfile.write("Temperature at Evaporator: " + str(TEvapOut + SupHeat)  + " K" + "\n")
    outfile.write("Enthalpy at Evaporator: " + str(H1) + " J/kg-K" + "\n")
    outfile.write("Entropy at Evaporator: " + str(S1) + " J" + "\n")
    outfile.write("Enthalpy at Economizer: " + str(H2) + " J" + "\n")
    #print("Temperature at Economizer: " + str(T2))
    outfile.write("\n")
    outfile.write("\n")
    outfile.write("STAGE 2" + "\n")
    outfile.write("FlowRate: " + str(FlowRate2) + " kg/s" + "\n")
    outfile.write("Pressure1: " + str(PCondOut) + " Pa" + "\n")
    outfile.write("Temperature1: " + str(T21) + " K" + "\n")
    outfile.write("Enthalpy1: " + str(H21) + " J" + "\n")
    outfile.write("Entropy1: " + str(S21) + " J/kg-K"+ "\n")
    outfile.write("Enthalpy2: " + str(H22) + " J")

    return None

input_list = []
with open('input.csv') as csvfile:
    reader = csv.reader(csvfile, delimiter=' ')
    for row in reader:
        if row[0] == 'Refrig':
            input_list.append(row[1])
        else:
            input_list.append(float(row[1]))
print(input_list)
RefrigCalc(input_list[0], input_list[1], input_list[2], input_list[3],
           input_list[4], input_list[5], input_list[6], input_list[7],
           input_list[8], input_list[9], input_list[10], input_list[11],
           input_list[12], input_list[13], input_list[14],)
