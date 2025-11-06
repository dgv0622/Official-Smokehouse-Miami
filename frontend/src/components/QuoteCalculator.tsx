import { useState } from 'react';
import { useScrollAnimation } from '@/hooks/use-scroll-animation';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';

const QuoteCalculator = () => {
  const { ref, isVisible } = useScrollAnimation();
  const [currentStep, setCurrentStep] = useState(1);
  const [formData, setFormData] = useState({
    eventType: '',
    guestCount: '',
    serviceLevel: '',
    menuNotes: '',
    name: '',
    email: '',
    phone: ''
  });
  const [showResults, setShowResults] = useState(false);

  const totalSteps = 5;
  const progress = (currentStep / totalSteps) * 100;

  const calculatePrice = () => {
    const guests = parseInt(formData.guestCount) || 50;
    let pricePerPerson = 25;
    
    if (formData.serviceLevel === 'standard') pricePerPerson = 40;
    if (formData.serviceLevel === 'premium') pricePerPerson = 60;
    
    return guests * pricePerPerson;
  };

  const handleNext = () => {
    if (currentStep < totalSteps) {
      setCurrentStep(currentStep + 1);
    } else {
      setShowResults(true);
    }
  };

  const handleBack = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  };

  const restartQuote = () => {
    setCurrentStep(1);
    setShowResults(false);
    setFormData({
      eventType: '',
      guestCount: '',
      serviceLevel: '',
      menuNotes: '',
      name: '',
      email: '',
      phone: ''
    });
  };

  if (showResults) {
    const estimatedPrice = calculatePrice();
    return (
      <div ref={ref} className={`transition-all duration-700 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'}`}>
        <div className="bg-gradient-calculator rounded-lg p-6 md:p-12 shadow-elegant border border-accent/20">
          <div className="text-center py-4 md:py-8">
            <h2 className="text-2xl md:text-3xl font-light mb-3 md:mb-4 text-foreground">Your Estimated Price</h2>
            <div className="text-4xl md:text-6xl font-extralight text-accent my-6 md:my-8">
              ${estimatedPrice.toLocaleString()}
            </div>
            <p className="text-sm md:text-base text-foreground/70 mb-6 md:mb-8">Based on {formData.guestCount} guests with {formData.serviceLevel} service</p>
            
            <div className="bg-black/40 border-l-4 border-accent p-4 md:p-6 rounded-lg text-left mb-6 md:mb-8">
              <h3 className="text-xl font-light mb-4 text-foreground">Recommended Package</h3>
              <ul className="space-y-2 text-foreground/80">
                <li className="flex items-center gap-2">
                  <span className="text-accent font-bold">✓</span> Premium BBQ meats selection
                </li>
                <li className="flex items-center gap-2">
                  <span className="text-accent font-bold">✓</span> Signature sides & fixings
                </li>
                <li className="flex items-center gap-2">
                  <span className="text-accent font-bold">✓</span> Professional service staff
                </li>
                <li className="flex items-center gap-2">
                  <span className="text-accent font-bold">✓</span> Complete setup & cleanup
                </li>
              </ul>
            </div>
            
            <p className="text-foreground/60 mb-6 text-sm">This is an estimate based on your responses. Final pricing will be confirmed after consultation.</p>
            
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button className="bg-gradient-gold hover:shadow-glow transition-all duration-300 hover:-translate-y-1 text-black px-8 py-6 text-sm tracking-widest uppercase font-semibold">
                Contact Us to Book
              </Button>
              <Button onClick={restartQuote} variant="outline" className="border-2 border-accent text-accent hover:bg-accent/10 px-8 py-6 text-sm tracking-widest uppercase">
                Start Over
              </Button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div ref={ref} className={`transition-all duration-700 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'}`}>
      <div className="bg-gradient-calculator rounded-lg p-12 shadow-elegant border border-accent/20">
        {/* Progress Bar */}
        <div className="w-full h-1 bg-black/40 mb-8 rounded-full overflow-hidden">
          <div 
            className="h-full bg-gradient-gold transition-all duration-300"
            style={{ width: `${progress}%` }}
          />
        </div>

        {/* Step 1: Event Type */}
        {currentStep === 1 && (
          <div className="space-y-6 animate-fade-in-up">
            <div className="text-accent text-xs font-semibold tracking-widest uppercase mb-2">Question 1 of 5</div>
            <h2 className="text-2xl font-light text-foreground mb-6">What type of event are you planning?</h2>
            <div className="grid grid-cols-2 gap-4">
              {['corporate', 'wedding', 'private', 'other'].map((type) => (
                <button
                  key={type}
                  onClick={() => setFormData({ ...formData, eventType: type })}
                  className={`p-6 border-2 rounded-lg transition-all duration-300 hover:border-faded-mustard hover:-translate-y-1 hover:shadow-card ${
                    formData.eventType === type ? 'border-faded-mustard bg-gradient-to-br from-amber-700/30 to-amber-600/30' : 'border-border/20 bg-amber-700/10'
                  }`}
                >
                  <span className="capitalize text-foreground">{type === 'corporate' ? 'Corporate Event' : type === 'private' ? 'Private Party' : type.charAt(0).toUpperCase() + type.slice(1)}</span>
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Step 2: Guest Count */}
        {currentStep === 2 && (
          <div className="space-y-6 animate-fade-in-up">
            <div className="text-accent text-xs font-semibold tracking-widest uppercase mb-2">Question 2 of 5</div>
            <h2 className="text-2xl font-light text-foreground mb-6">How many guests are you expecting?</h2>
            <Input
              type="number"
              placeholder="Enter number of guests"
              value={formData.guestCount}
              onChange={(e) => setFormData({ ...formData, guestCount: e.target.value })}
              className="text-lg p-6 border-2 focus:border-faded-mustard bg-gradient-to-br from-amber-700/10 to-amber-600/10 text-foreground placeholder:text-foreground/40"
              min="1"
            />
          </div>
        )}

        {/* Step 3: Service Level */}
        {currentStep === 3 && (
          <div className="space-y-6 animate-fade-in-up">
            <div className="text-accent text-xs font-semibold tracking-widest uppercase mb-2">Question 3 of 5</div>
            <h2 className="text-2xl font-light text-foreground mb-6">What level of service do you prefer?</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {[
                { value: 'basic', title: 'Essential', desc: 'Disposable ware, 2hr service' },
                { value: 'standard', title: 'Executive', desc: 'Premium ware, staff, 4hr' },
                { value: 'premium', title: 'Prestige', desc: 'Full service, unlimited time' }
              ].map((level) => (
                <button
                  key={level.value}
                  onClick={() => setFormData({ ...formData, serviceLevel: level.value })}
                  className={`p-6 border-2 rounded-lg transition-all duration-300 hover:border-faded-mustard hover:-translate-y-1 hover:shadow-card ${
                    formData.serviceLevel === level.value ? 'border-faded-mustard bg-gradient-to-br from-amber-700/30 to-amber-600/30' : 'border-border/20 bg-amber-700/10'
                  }`}
                >
                  <div className="font-medium text-foreground mb-2">{level.title}</div>
                  <div className="text-sm text-foreground/60">{level.desc}</div>
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Step 4: Menu Notes */}
        {currentStep === 4 && (
          <div className="space-y-6 animate-fade-in-up">
            <div className="text-accent text-xs font-semibold tracking-widest uppercase mb-2">Question 4 of 5</div>
            <h2 className="text-2xl font-light text-foreground mb-6">Any special menu requirements?</h2>
            <Textarea
              placeholder="Dietary restrictions, preferred meats, special requests..."
              value={formData.menuNotes}
              onChange={(e) => setFormData({ ...formData, menuNotes: e.target.value })}
              className="min-h-32 text-lg p-4 border-2 focus:border-faded-mustard bg-gradient-to-br from-amber-700/10 to-amber-600/10 text-foreground placeholder:text-foreground/40"
              rows={4}
            />
          </div>
        )}

        {/* Step 5: Contact Info */}
        {currentStep === 5 && (
          <div className="space-y-6 animate-fade-in-up">
            <div className="text-accent text-xs font-semibold tracking-widest uppercase mb-2">Question 5 of 5</div>
            <h2 className="text-2xl font-light text-foreground mb-6">How can we reach you?</h2>
            <div className="space-y-4">
              <Input
                type="text"
                placeholder="Your name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className="text-lg p-6 border-2 focus:border-faded-mustard bg-gradient-to-br from-amber-700/10 to-amber-600/10 text-foreground placeholder:text-foreground/40"
              />
              <Input
                type="email"
                placeholder="Your email"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                className="text-lg p-6 border-2 focus:border-faded-mustard bg-gradient-to-br from-amber-700/10 to-amber-600/10 text-foreground placeholder:text-foreground/40"
              />
              <Input
                type="tel"
                placeholder="Your phone number"
                value={formData.phone}
                onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                className="text-lg p-6 border-2 focus:border-faded-mustard bg-gradient-to-br from-amber-700/10 to-amber-600/10 text-foreground placeholder:text-foreground/40"
              />
            </div>
          </div>
        )}

        {/* Navigation Buttons */}
        <div className="flex gap-4 mt-8">
          <Button
            onClick={handleBack}
            variant="secondary"
            className={`flex-1 px-6 py-6 tracking-widest uppercase text-sm bg-black/40 hover:bg-black/60 text-foreground border border-accent/20 ${currentStep === 1 ? 'invisible' : ''}`}
          >
            Back
          </Button>
          <Button
            onClick={handleNext}
            className="flex-1 bg-gradient-gold hover:shadow-glow transition-all duration-300 hover:-translate-y-1 text-black px-6 py-6 tracking-widest uppercase text-sm font-semibold"
          >
            {currentStep === totalSteps ? 'Get My Estimate' : 'Next'}
          </Button>
        </div>
      </div>
    </div>
  );
};

export default QuoteCalculator;
