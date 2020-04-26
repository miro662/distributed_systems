module SmartHouse {
    struct Color {
        float r;
        float g;
        float b;
    };

    struct Range {
        float min;
        float max;
    };

    enum Mode {
        Blink,
        Sine,
        Still
    };

    exception InvaildColorException {};
    exception UnsupportedFrequency {};

    interface LightBulb {
        idempotent bool getState();
        void setState(bool newState);
    };

    interface RGBBulb extends LightBulb {
        idempotent Color getColor();
        void setColor(Color color) throws InvaildColorException;
    };

    interface StroboscopeBulb extends LightBulb {
        idempotent Range getSupportedFrequenciesRange();
        idempotent float getFrequency();
        void setFrequency(float newFrequency) throws UnsupportedFrequency;
        void setMode(Mode newMode);
    };

    interface Thermometer {
        idempotent float getTemperature();
        idempotent Range getSuportedRange();
    };

    interface Bulbulator {
        string mumble();
    };
};