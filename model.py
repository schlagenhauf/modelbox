class Model:
    def __init__(self,name):
        self.name = name
        self.props = {}
        self.modelRef = None


    def getPropNames(self):
        return self.props.keys()


    ##
    # @brief Set a model property
    #
    # @param key Property name
    # @param value Property value
    def setProperty(self, key, value):
        # TODO: handle missing keys
        self.props[key] = value


    ##
    # @brief Apply changed properties to 3d model
    def update(self):
        pass
