import { useEffect, useRef } from 'react';
import { Button } from '@/components/ui/button';

const Hero = () => {
  const heroRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Fade in animation on load
    const timer = setTimeout(() => {
      if (heroRef.current) {
        heroRef.current.style.opacity = '1';
      }
    }, 100);

    return () => clearTimeout(timer);
  }, []);

  const scrollToCalculator = () => {
    const calculator = document.getElementById('calculator');
    calculator?.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <section 
      ref={heroRef}
      className="relative min-h-screen flex items-center justify-center overflow-hidden transition-opacity duration-1000 opacity-0"
      style={{ minHeight: 'calc(100vh - 4rem)' }}
    >
      {/* Background with film grain effect */}
      <div className="absolute inset-0 bg-gradient-to-br from-burnt-umber via-charcoal-gray to-burnt-umber opacity-95" />
      
      {/* Subtle smoke drift overlay */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 left-1/3 w-[600px] h-[600px] bg-faded-mustard/10 rounded-full blur-[150px] animate-pulse" 
             style={{ animationDuration: '8s' }} />
        <div className="absolute bottom-1/3 right-1/4 w-[500px] h-[500px] bg-cream-white/5 rounded-full blur-[120px] animate-pulse" 
             style={{ animationDuration: '10s', animationDelay: '2s' }} />
      </div>

      {/* Film grain texture overlay */}
      <div 
        className="absolute inset-0 opacity-[0.08] mix-blend-overlay pointer-events-none"
        style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 300 300' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='3' numOctaves='4' /%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E")`,
          backgroundSize: '300px 300px'
        }}
      />

      {/* Content */}
      <div className="relative z-10 text-center px-4 md:px-6 max-w-5xl mx-auto">
        {/* Main Headline */}
        <h1 
          className="text-4xl sm:text-5xl md:text-7xl lg:text-8xl font-serif text-cream-white mb-4 md:mb-6 tracking-wide leading-tight animate-in fade-in-up duration-1000"
          style={{ animationDelay: '300ms', animationFillMode: 'backwards' }}
        >
          Real Food. Real Values.
          <br />
          <span className="text-faded-mustard">Done Right.</span>
        </h1>

        {/* Subtext */}
        <p 
          className="text-base md:text-lg lg:text-xl text-cream-white/80 mb-8 md:mb-10 tracking-wide font-light max-w-2xl mx-auto leading-relaxed animate-in fade-in-up duration-1000"
          style={{ animationDelay: '600ms', animationFillMode: 'backwards' }}
        >
          Heritage and craftsmanship meet modern hospitality. 
          <br className="hidden md:block" />
          Slow-smoked over post oak, served with heart.
        </p>

        {/* CTA Button */}
        <div 
          className="animate-in fade-in-up duration-1000"
          style={{ animationDelay: '900ms', animationFillMode: 'backwards' }}
        >
          <Button
            onClick={scrollToCalculator}
            size="lg"
            className="h-12 md:h-14 px-8 md:px-10 bg-burnt-umber hover:bg-burnt-umber/90 text-cream-white text-sm md:text-base tracking-wide font-medium rounded shadow-lg hover:shadow-xl transition-all duration-300 border border-faded-mustard/30"
          >
            Plan Your Feast
          </Button>
        </div>
      </div>
    </section>
  );
};

export default Hero;
