Stock Inventory Count
#####################

Implements several feautures for Inventory counting.

One field is added to Product Template:

- Unit of Count: The unit of product counting.


Fields added to Inventory Line:

    - Unit 1: The first unit of count (required).
      If Unit of count is not defined for product, default product Unit is used.
    - Quantity 1: The quantiry for Unit 1.
    - Unit 2: The second unit of count. It is optional.
    - Quantity 2: The quantiry for Unit 2. Required if Unit 2 is set.
