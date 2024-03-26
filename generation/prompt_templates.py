few_shot = """
        - Example 1
        Design: Bicycle Frame
        Criterion: Impact Resistant
        You are tasked with designing the grip of a bicycle frame which should be impact resistant.
        How well do you think each of the provided materials would perform in this application? (Use a scale of 0-10 where 0 is 'unsatisfactory', 5 is 'acceptable', and 10 is 'excellent')
    
        Steel: 6 
        Steel, known for its durability and high hardness, offers good impact resistance. However, due to its thermal conductivity, it can feel cold in extreme weather conditions. The economical viability of creating complex grip geometries in steel might not be as advantageous compared to other options. Additionally, steel grips can be quite heavy, adding to the weight of the bike.
        
        Aluminium: 5 
        Aluminium is lighter than steel and provides reasonable impact resistance. That said, similar to steel, it may not be the most comfortable material for a grip for the same thermal comfort reasons.
        
        Titanium: 4 
        Titanium, a fusion of steel's strength and aluminium's lightness, is a decent choice for impact resistance. However, its efficacy as a comfortable grip is debatable.
        
        Glass: 2 
        Glass is a less-than-ideal choice for a bicycle grip. With low impact resistance and a high risk of shattering, it poses significant safety concerns.
        
        Wood: 8 
        Wood offers a comfortable grip and has decent impact resistance. However, it might degrade over time and may not endure harsh weather conditions well. Additionally, wood grips might require maintenance, like oiling, to preserve their lifespan.
        
        Thermoplastic: 9 
        Thermoplastics, such as polyurethane or nylon, provide excellent impact resistance and can be molded for a comfortable grip. Not to mention, they are durable and weather-resistant.
        
        Elastomer: 9 
        Elastomers, like rubber, are ideal for grips due to their high impact resistance and comfort. They can be designed for optimal grip and shock absorption. Their compliance also makes them a good
        
        Thermoset: 6 
        Thermosets are hard and durable, offering decent impact resistance. However, their comfort level may not be as high as that of thermoplastics or elastomers.
        
        Composite: 7 
        Composite materials, when designed well, can offer high impact resistance and a comfortable grip. Their performance, however, depends on the specific materials used in the composite.
    
    
        - Example 2
        Design: Medical Implant
        Criterion: Durable
        You are tasked with designing a medical implant which should be durable. How well do you
        think each of the provided materials would perform in this application? (Use a scale of 0-10 where 0 is 'unsatisfactory', 5 is 'acceptable', and 10 is 'excellent')
        
        Steel: 7 
        Medical-grade steel is highly durable, making it a reasonable choice. However, consider its density, as steel is heavier than other options.

        Aluminium: 2 
        Aluminium, due to toxicity and biocompatibility issues, is generally not used in implants. While it can be coated to improve its biocompatibility, it's not the most practical choice.

        Titanium: 9 
        Titanium alloys are a go-to for medical implants, thanks to their high strength, low density, and excellent biocompatibility. Additive manufacturing processes enable the creation of complex geometries, further improving biocompatibility. Additionally, titanium is corrosion-resistant, a crucial property for implants within the body.

        Glass: 5 
        While glass is generally brittle and unsuitable for most implants, Bioglasses, a specific type of bioactive glasses, have been used successfully in certain medical applications. Despite this, their mechanical properties can limit their use, requiring careful consideration for each specific scenario.

        Wood: 0 
        Wood is not an appropriate material for medical implants. It lacks the needed durability and poses a high risk of infection.

        Thermoplastic: 8 
        Certain medical-grade thermoplastics are used in implants for their durability. However, careful selection is necessary to ensure biocompatibility and withstand sterilization processes. Selection factors include chemical resistance and fatigue strength, important for long-term implant functionality.

        Elastomer: 8 
        Medical-grade elastomers, like silicone, are quite durable and are often used in implants, especially for soft tissue replacements.

        Thermoset: 7 
        Thermosets are hard and durable, but their biocompatibility depends on the specific type used. There are other more appropriate materials.

        Composite: 7 
        Composite materials, properly designed, can offer high durability and biocompatibility. However, their suitability and performance are highly dependant on the materials used to form the composite.\n\n
        """