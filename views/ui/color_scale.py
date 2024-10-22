class ColorScale:
    color_scale = "bw" 
    @classmethod
    def set_color_scale(cls, scale):
        cls.color_scale = scale

    @classmethod
    def get_color_scale(cls):
        return cls.color_scale