def build_layers(params, num_of_layers, MAX_TOT_THICKNESS):
    total_thickness_orig = sum(float(params[i]) for i in range(2, len(params), 2))
    result = []
    accum = 0.0
    for i in range(num_of_layers):
        allowed = MAX_TOT_THICKNESS - accum
        if allowed <= 0:
            #print("["+str(i)+"] omitted")
            break

        material = params[1 + 2*i]
        thickness = float(params[2 + 2*i])
        clipped = min(thickness, allowed)
        #if allowed < thickness:
        #    print("["+str(i)+"] clipped")

        if clipped > 0.0:
            result.append({"material": material, "thickness": clipped})
            accum += clipped

        if accum >= MAX_TOT_THICKNESS:
            break

    total_thickness_clipped = sum(layer["thickness"] for layer in result)
    if (total_thickness_clipped < total_thickness_orig):
        print("clipped!")
 
    return result

def main():
    # Case 1: total under limit
    params = ["skip", "Al", 1.0, "Cu", 2.0, "Pb", 3.0]
    print("Case 1:", build_layers(params, 3, 10.0))
    print("xxxxxxxxxxxx\n\n")

    # Case 2: exactly at limit after second layer
    params = ["skip", "Al", 4.0, "Cu", 6.0, "Pb", 3.0]
    print("Case 2:", build_layers(params, 3, 10.0))
    print("xxxxxxxxxxxx\n\n")

    # Case 3: over limit at second layer -> second is clipped; third omitted
    params = ["skip", "Al", 4.0, "Cu", 7.0, "Pb", 3.0]
    print("Case 3:", build_layers(params, 3, 10.0))
    print("xxxxxxxxxxxx\n\n")

    # Case 4: first layer alone exceeds limit -> first clipped; others omitted
    params = ["skip", "Al", 12.0, "Cu", 2.0]
    print("Case 4:", build_layers(params, 2, 10.0))
    print("xxxxxxxxxxxx\n\n")

if __name__ == "__main__":
    main()

