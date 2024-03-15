few_shot = """
        - Example 1
        Design: Bicycle Frame
        Criterion: Lightweight
        You are tasked with designing the frame of a bicycle which should be lightweight. How well do you
        think each of the provided materials would perform in this application? (Use a scale of 0-10 and the 
        materials are: 
    
        Steel: 4
        Steel has the highest density of all options available so not immediately suitable for light 
        weighting. Despite its high tensile strength, the specific strength of steel is lower than that of other 
        material options and thus not a suitable option.
        
        Aluminium: 9
        Aluminium has the lowest density of metals/alloys in this selection making it an 
        ideal candidate for light-weighting a structural frame. It has a lower specific strength compared to 
        titanium alloys suggesting more material would be required to achieve an equivalent strength. 
        
        Titanium: 8
        titanium as a stand-alone material is not a suitable for this application. Its alloys 
        however can enhance its mechanical strength significantly making it an ideal candidate for this 
        application, second only to thermoset composites.
        
        Glass: 3
        Glass, specifically silicates, have a lower density than most metals/alloys and also have 
        higher mechanical strength however they are typically very brittle, making them less suitable for a 
        lightweight bicycle frame.
        
        Wood: 6
        Wood materials such as bamboo can be relatively light and can be used for bicycle 
        frames. Denser woods such as pine or oak can be quite heavy compared to other alternatives as their
        shape is generally limited to solid volumes. Woods have anisotropic mechanical properties which 
        limits how they can be used.
        
        Thermoplastic: 7
        thermoplastics cover a broad range of polymeric materials. Some examples 
        such as nylon and PET have a low density and sufficiently high stiffness to be a viable option. A 
        low glass transition temperature might affect the materials rigidity and thus suitability for this 
        application.
        
        Elastomer: 1
        Elastomers are characterised by their high ductility in the elastic deformation. 
        While some rigid elastomers such as some polyurethanes exist, these materials are generally 
        unsuitable for the application.
        
        Thermoset Composite: 10
        These materials, specifically carbon fibre epoxy, combine low density 
        with the stiffest materials available to create a composite structure which combines the best 
        properties of two or more materials. As a result, the specific strength for this class of materials is the
        highest meaning it is the most suitable for this application.
    
    
        - Example 2
        Design: Bicycle Frame
        Criterion: High Strength 
        You are tasked with designing the frame of a bicycle which should be lightweight. How well do you
        think each of the provided materials would perform in this application? (Use a scale of 0-10 and the 
        materials are: 
        
        Steel: 9
        Steel has a good balance of high strength and stiffness making it highly suited for 
        maximising strength of the design.
        
        Aluminium: 7
        Aluminium has a good strength-to-weight ratio (specific strength) but is not as 
        strong as steel or titanium. Its strength can be enhanced through alloying and heat treatment. 
        However, it may not be as durable under high stress conditions compared to steel or titanium.
        
        Titanium: 8
        Titanium has a higher strength-to-weight ratio (specific strength) than aluminium and
        is comparable to some types of steel. It also has excellent fatigue resistance, which is important for 
        a bicycle frame that will undergo repeated stress cycles.
        
        Glass: 3
        Glass has low tensile strength and is brittle, making it less suitable for applications that 
        require high strength. While it can be used in certain types of composite materials to increase 
        strength, it's not typically used on its own for high-strength applications.
        
        Wood: 6
        Wood can have good strength depending on the type and treatment, but it's generally not
        as strong as metals and may not have the same level of consistency and durability. It can be used for
        bicycle frames, but may not be the best choice for high-strength applications.
        
        Thermoplastic: 7
        The strength of thermoplastics can vary greatly depending on the type. Some 
        high-performance thermoplastics can have good strength, but they generally can't match the 
        strength of metals or high-performance composites. The glass transition temperature can also 
        influence the strength of the thermoplastic, low glass transition typically translates to reduced 
        stiffness and strength.
        
        Elastomer: 1
        Elastomers are not typically used for high-strength applications. They are better 
        suited for applications that require flexibility and shock absorption.
        
        Thermoset Composite: 10
        High-performance thermoset composites, especially those reinforced 
        with materials like carbon fibre, aramids or glass, can have excellent strength and stiffness while 
        also being lightweight. They are an excellent choice for high-strength applications.\n\n
        """