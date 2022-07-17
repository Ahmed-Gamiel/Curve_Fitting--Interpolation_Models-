class Function:
    def function( order, coef):
        if order == 10:
            return ("(" + str((round(coef[0],3))) + "X¹⁰) + " + "(" + str((round(coef[1],3))) + "X⁹) + " + "(" + str(
                (round(coef[2],3))) + "X⁸) + " + "(" + str((round(coef[3],3))) + "X⁷) + " + "(" + str(
                (round(coef[4],3))) + "X⁶) + " + "(" + str((round(coef[5],3))) + "X⁵) + " + "(" + str(
                (round(coef[6],3))) + "X⁴)" + "(" + str((round(coef[7],3))) + "X³)" + str((round(coef[8],3))) + "X²)" + str((round(coef[9]))) + "X)"
                    + str((round(coef[10]))) + ")")
        if order == 9:
            return ("(" + str((round(coef[0],3))) + "X⁹) + " + "(" + str((round(coef[1],3))) + "X⁸) + " + "(" + str(
                (round(coef[2],3))) + "X⁷) + " + "(" + str((round(coef[3],3))) + "X⁶) + " + "(" + str(
                (round(coef[4],3))) + "X⁵) + " + "(" + str((round(coef[5],3))) + "X⁴) + " + "(" + str(
                (round(coef[6],3))) + "X³)" + "(" + str((round(coef[7],3))) + "X²)" + str((round(coef[8],3))) + "X)" + str((round(coef[9],3))) + ")")
        if order == 8:
            return ("(" + str((round(coef[0],3))) + "X⁸) + " + "(" + str((round(coef[1],3))) + "X⁷) + " + "(" + str(
                (round(coef[2],3))) + "X⁶) + " + "(" + str((round(coef[3],3))) + "X⁵) + " + "(" + str(
                (round(coef[4],3))) + "X⁴) + " + "(" + str((round(coef[5],3))) + "X³) + " + "(" + str(
                (round(coef[6],3))) + "X²)" + "(" + str((round(coef[7],3))) + "X)" + str((round(coef[8],3))) + ")")
        if order == 7:
            return ("(" + str((round(coef[0],3))) + "X⁷) + " + "(" + str((round(coef[1],3))) + "X⁶) + " + "(" + str(
                (round(coef[2],3))) + "X⁵) + " + "(" + str((round(coef[3],3))) + "X⁴) + " + "(" + str(
                (round(coef[4],3))) + "X³) + " + "(" + str((round(coef[5],3))) + "X²) + " + "(" + str(
                (round(coef[6],3))) + "X)" + "(" + str((round(coef[7],3))) + ")")

        if order == 6:
            return ("(" + str((round(coef[0],3))) + "X⁶) + " + "(" + str((round(coef[1],3))) + "X⁵) + " + "(" + str(
                (round(coef[2],3))) + "X⁴) + " + "(" + str((round(coef[3],3))) + "X³) + " + "(" + str(
                (round(coef[4],3))) + "X²) + " + "(" + str((round(coef[5],3))) + "X) + " + "(" + str(
                (round(coef[6],3))) + ")")
        elif order == 5:
            return ("(" + str(round(coef[0],3)) + "X⁵) + " + "(" + str(round(coef[1],3)) + "X⁴) + " + "(" + str(
                round(coef[2],3)) + "X³) + " + "(" + str(round(coef[3],3)) + "X²) + " + "(" + str(
                round(coef[4],3)) + "X) + " + "(" + str(round(coef[5],3)) + ")")
        elif order == 4:
            return ("(" + str(round(coef[0],3)) + "X⁴) + " + "(" + str(round(coef[1],3)) + "X³) + " + "(" + str(
                round(coef[2],3)) + "X²) + " + "(" + str(round(coef[3],3)) + "X) + " + "(" + str(
                round(coef[4],3)) + ")")
        elif order == 3:
            return ("(" + str(round(coef[0],3)) + "X³) + " + "(" + str(round(coef[1],3)) + "X²) + " + "(" + str(
                round(coef[2],3)) + "X) + " + "(" + str(round(coef[3],3)) + ")")
        elif order == 2:
            return ("(" + str(round(coef[0],3)) + "X²) + " + "(" + str(round(coef[1],3)) + "X) + " + "(" + str(
               round(coef[2],3)) + ")")
        else:
            return "(" + str(round(coef[0],3)) + "X) + " + "(" + str(round(coef[1],3)) + ")"