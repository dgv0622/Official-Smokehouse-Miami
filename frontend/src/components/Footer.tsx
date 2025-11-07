const Footer = () => {
  const scrollToSection = (id: string) => {
    const element = document.getElementById(id);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <footer className="bg-charcoal-gray text-cream-white py-16 border-t-2 border-faded-mustard">
      <div className="max-w-7xl mx-auto px-6 lg:px-12">
        {/* Main Footer Content */}
        <div className="grid md:grid-cols-3 gap-12 mb-12">
          {/* Brand */}
          <div className="space-y-4">
            <div className="flex items-center gap-3">
              <img
                src="/logo.png"
                alt="Smokehouse Miami Logo"
                className="h-16 w-auto"
              />
              <h3 className="text-2xl font-serif text-faded-mustard">Smokehouse Miami</h3>
            </div>
            <p className="text-cream-white/70 text-sm leading-relaxed">
              Proudly smoked in Texas tradition, served with Miami heart.
              Real wood, real time, real BBQ.
            </p>
            <div className="flex gap-3 text-xs text-cream-white/60">
              <span className="border-r border-cream-white/30 pr-3">Family Owned</span>
              <span className="border-r border-cream-white/30 pr-3">Post Oak Smoked</span>
              <span>Since 2012</span>
            </div>
          </div>

          {/* Quick Links */}
          <div className="space-y-4">
            <h4 className="text-sm uppercase tracking-[0.2em] text-faded-mustard font-medium">Quick Links</h4>
            <div className="flex flex-col gap-2">
              {[
                { id: 'menu', label: 'Our Menu' },
                { id: 'calculator', label: 'Get a Quote' },
                { id: 'chat-config', label: 'Contact Us' }
              ].map((item) => (
                <button
                  key={item.id}
                  onClick={() => scrollToSection(item.id)}
                  className="text-cream-white/70 hover:text-faded-mustard transition-colors duration-200 text-left text-sm"
                >
                  {item.label}
                </button>
              ))}
            </div>
          </div>

          {/* Contact */}
          <div className="space-y-4">
            <h4 className="text-sm uppercase tracking-[0.2em] text-faded-mustard font-medium">Get in Touch</h4>
            <div className="space-y-2 text-sm text-cream-white/70">
              <p>Miami, Florida</p>
              <p>degv@smokehouse-miami.com</p>
              <p>(305) 282-2105</p>
              <p>(305) 281-4632</p>
            </div>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="pt-8 border-t border-cream-white/10">
          <div className="flex flex-col md:flex-row justify-between items-center gap-4 text-sm text-cream-white/60">
            <p>&copy; 2025 Smokehouse Miami. All rights reserved.</p>
            <p className="italic font-light">
              "Slow-smoked patience, served with pride"
            </p>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
