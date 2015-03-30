#include <math.h>

const double lt = 10.0;
const double ls = 10.0;

const double kt  = 1.0; // Higher spring constant -> less deviation from equilibrium
const double kml = 1.0;
const double kmr = 1.0;
const double kbl = 1.0;
const double kbr = 1.0;
	
const double mb = 1.0; // Higher mass constant -> less movement
const double mm = 1.0;
const double mt = 1.0;

const double ba = (108.0 / 180) * M_PI;
const double ma = (108.0 / 180) * M_PI;
const double ta = (108.0 / 180) * M_PI;

const double bla_init = (108.0 / 180) * M_PI;
const double mla_init = (36.0 / 180) * M_PI;
const double mra_init = (36.0 / 180) * M_PI;
const double bra_init = (100.0 / 180) * M_PI;

const double inctime = 0.1;
const double runtime = 10000.0;

extern double fblx, fbly;		// Brownian variables
extern double fmlx, fmly;
extern double ftx, fty;
extern double fmrx, fmry;
extern double fbrx, fbry;

typedef enum {
	LEFTBOUND,
	RIGHTBOUND,
	BOTHBOUND
} states;


/* ******************************** DYNEIN CLASS DEFINITION *************************************** */

class Dynein {
	public:
		void set_bla(double d);
		void set_mla(double d);
		void set_mra(double d);
		void set_bra(double d);
		
		void set_blx(double d);
		void set_bly(double d);
		
		void set_state(states s);
		
		void set_d_bla(double d);
		void set_d_mla(double d);
		void set_d_mra(double d);
		void set_d_bra(double d);
		
		double get_bly();
		double get_blx();
		double get_mlx();
		double get_mly();
		double get_tx();
		double get_ty();
		double get_mrx();
		double get_mry();
		double get_brx();
		double get_bry();
		
		double get_bla();
		double get_mla();
		double get_mra();
		double get_bra();
		
		double get_d_bla();
		double get_d_mla();
		double get_d_mra();
		double get_d_bra();
		
		double get_d_blx();
		double get_d_mlx();
		double get_d_mrx();
		double get_d_brx();
		
		double get_d_bly();
		double get_d_mly();
		double get_d_mry();
		double get_d_bry();
		
		double get_dd_bla();
		double get_dd_mla();
		double get_dd_mra();
		double get_dd_bra();
		
		double get_dd_blx();
		double get_dd_mlx();
		double get_dd_mrx();
		double get_dd_brx();
		
		double get_dd_bly();
		double get_dd_mly();
		double get_dd_mry();
		double get_dd_bry();
		
		double get_PE();
		double get_KE();
		
		states get_state();
		
		void log(double t);
		
	private:
		double bla;
		double mla;
		double mra;
		double bra;
	
		double d_bla; //Angular Velocities
		double d_mla;
		double d_mra;
		double d_bra;
		
		double blx;
		double bly;
		
		states state;
};

/* *********************************** UTILITY PROTOTYPES ****************************************** */
double randAngle(double range);
double dist(double d, double h, double i, double j);
void   resetLog(Dynein* dyn);
double square(double num);
double cube(double num);
double fifth(double num);