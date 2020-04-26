using System;
using System.Collections.Generic;
using Ice;

namespace Server
{
    public class BulbulatorI : SmartHouse.BulbulatorDisp_
    {
        public override string mumble(Current current = null)
        {
            var message = "bul bul bul";
            Console.WriteLine("[" + current.id.name + "] " + message);
            return message;
        }
    }

    public class LightBulbI : SmartHouse.LightBulbDisp_ {
        private bool status;

        public override bool getState(Current current = null) => status;
        public override void setState(bool newState, Current current = null) => this.status = newState;
    }

    public class RGBBulbI : SmartHouse.RGBBulbDisp_ {
        private bool status;
        private SmartHouse.Color color;

        public override bool getState(Current current = null) => status;
        public override void setState(bool newState, Current current = null) => this.status = newState;

        public override void setColor(SmartHouse.Color color, Current current = null) {
            if (color.r < 0 || color.r > 1 || color.g < 0 || color.g > 1 || color.b < 0 || color.b > 1) {
                throw new SmartHouse.InvaildColorException();
            }

            this.color = color;
        }
        public override SmartHouse.Color getColor(Current current = null) => this.color;        
    }

    public class ThermometerI : SmartHouse.ThermometerDisp_
    {
        private SmartHouse.Range range = new SmartHouse.Range(-50.0f, 150.0f);

        public ThermometerI(SmartHouse.Range range) {
            this.range = range;
        }

        public override SmartHouse.Range getSuportedRange(Current current = null) => range;

        public override float getTemperature(Current current = null)
        {
            Random rng = new Random();
            return ((float) rng.NextDouble()) * (range.max - range.min) + range.min;
        }
    }

    public class StroboscopeBulbI : SmartHouse.StroboscopeBulbDisp_ {
        private bool status;
        private float frequency = 10.0f;
        private SmartHouse.Mode mode = SmartHouse.Mode.Still;
        private SmartHouse.Range supportedFrequencies = new SmartHouse.Range(1.0f, 10.0f);
        
        public override bool getState(Current current = null) => status;
        public override void setState(bool newState, Current current = null) => this.status = newState;

        public override void setFrequency(float newFrequency, Current current = null) {
            if (newFrequency <= supportedFrequencies.min || newFrequency >= supportedFrequencies.max)
                throw new SmartHouse.UnsupportedFrequency();
            
            this.frequency = newFrequency;
        }
        public override float getFrequency(Current current = null) => this.frequency;
        public override SmartHouse.Range getSupportedFrequenciesRange(Current current = null) => this.supportedFrequencies;

        public override void setMode(SmartHouse.Mode newMode, Current current = null) => this.mode = newMode;
    }

    interface IServantSource {
        Ice.Object GetServant();
    }

    delegate Ice.Object ServantFactory();

    class LazyServant : IServantSource {
        private bool instantiated;
        private Ice.Object servant;
        private ServantFactory factory;

        public LazyServant(ServantFactory factory) {
            this.factory = factory;
        }

        public Ice.Object GetServant()
        {
            if (!instantiated)
            {
                servant = this.factory();
                instantiated = true;
            }
            return servant;
        }
    }

    class SmartHouseServantLocator : ServantLocator
    {
        private Dictionary<string, IServantSource> servants = new Dictionary<string, IServantSource>();

        public void deactivate(string category) {}

        public void finished(Current curr, Ice.Object servant, object cookie) {}

        public Ice.Object locate(Current curr, out object cookie)
        {
            cookie = null;
            return servants.GetValueOrDefault(curr.id.name)?.GetServant();
        }

        public SmartHouseServantLocator() {
            servants.Add("Bulbulator1", new LazyServant(() => new BulbulatorI()));
            servants.Add("Bulbulator2", new LazyServant(() => new BulbulatorI()));

            servants.Add("Bulb", new LazyServant(() => new LightBulbI()));
            servants.Add("RGBBulb", new LazyServant(() => new RGBBulbI()));
            servants.Add("StroboscopeBulb", new LazyServant(() => new StroboscopeBulbI()));

            servants.Add("Thermometer1", new LazyServant(() => new ThermometerI(new SmartHouse.Range(-50.0f, 50.0f))));
            servants.Add("Thermometer2", new LazyServant(() => new ThermometerI(new SmartHouse.Range(0.0f, 100.0f))));
        }
    }

    class Program
    {
        public static int Main(string[] args)
        {
            try
            {
                using(Ice.Communicator communicator = Ice.Util.initialize(ref args))
                {
                    var adapter =
                        communicator.createObjectAdapterWithEndpoints("SmartHouseAdapter", "default -h localhost -p 10000");
                    
                    SmartHouseServantLocator sl = new SmartHouseServantLocator();
                    adapter.addServantLocator(sl, "");
                    adapter.activate();
                    communicator.waitForShutdown();
                }
            }
            catch (System.Exception e)
            {
                Console.Error.WriteLine(e);
                return 1;
            }
            return 0;
        }
    }
}
