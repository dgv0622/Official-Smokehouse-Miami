import { useScrollAnimation } from '@/hooks/use-scroll-animation';

const locations = [
  'Kendall',
  'Coral Gables',
  'Pinecrest',
  'Homestead',
  'Brickell',
  'Miami Beach',
  'Hialeah',
  'Doral',
  'Pembroke Pines',
];

const Locations = () => {
  const { ref, isVisible } = useScrollAnimation();

  return (
    <section className="py-24 md:py-32 bg-gradient-to-b from-cream-white to-burnt-umber/5 relative overflow-hidden" id="locations">
      {/* Subtle texture overlay */}
      <div 
        className="absolute inset-0 opacity-[0.03] mix-blend-multiply"
        style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence baseFrequency='0.65' /%3E%3C/filter%3E%3Crect width='60' height='60' filter='url(%23noise)'/%3E%3C/svg%3E")`,
        }}
      />

      <div className="max-w-4xl mx-auto px-6 relative z-10">
        <div 
          ref={ref}
          className={`text-center transition-all duration-1000 ${
            isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-12'
          }`}
        >
          {/* Header */}
          <div className="mb-12">
            <p className="text-faded-mustard text-sm uppercase tracking-[0.2em] font-medium mb-3">
              Proudly Serving
            </p>
            <h2 className="text-4xl md:text-5xl font-serif text-charcoal-gray tracking-wide leading-tight mb-4">
              Service Locations
            </h2>
            <div className="w-16 h-0.5 bg-burnt-umber/30 mx-auto" />
          </div>

          {/* Locations List - 3 per row */}
          <div className="space-y-6">
            {Array.from({ length: Math.ceil(locations.length / 3) }).map((_, rowIndex) => (
              <div 
                key={rowIndex}
                className="flex items-center justify-center gap-6 animate-in fade-in-up duration-700"
                style={{ animationDelay: `${rowIndex * 150}ms`, animationFillMode: 'backwards' }}
              >
                {locations.slice(rowIndex * 3, rowIndex * 3 + 3).map((location, colIndex) => (
                  <>
                    <p 
                      key={location}
                      className="text-2xl md:text-3xl font-serif text-burnt-umber tracking-wide italic"
                    >
                      {location}
                    </p>
                    {colIndex < 2 && rowIndex * 3 + colIndex < locations.length - 1 && (
                      <span className="text-burnt-umber/40 text-xl">•</span>
                    )}
                  </>
                ))}
              </div>
            ))}
          </div>

          {/* Footer Note */}
          <div className="mt-16 pt-8 border-t border-burnt-umber/10">
            <p className="text-sm text-charcoal-gray/60 italic">
              Bringing authentic BBQ to your neighborhood
            </p>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Locations;
