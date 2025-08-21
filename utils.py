#utils.py
#misc. helper functions

import DEFINES

from functools import wraps
import logging

log = logging.getLogger(__name__)


def manufacturer_adjust_set_position(fn):
    """
    Wraps a set_position(alpha,beta) so that if the manufacturer is 
    'Orbray' (trillium mechanism), the angles are adjusted by the 
    gearbox ratio of the Orbray positioners.
    """
    @wraps(fn)
    def wrapper(self,alpha, beta, *, manufacturer=None):
        manufacturer = getattr(DEFINES, "MANUFACTURER", None)
        #here we use a global variable for backwards compatibility reasons
        if manufacturer and manufacturer.lower() == "orbray":
            alpha_adjusted = alpha * DEFINES.SDSS_TO_ORBRAY_GEAR_RATIO * DEFINES.PROTO_21_ORBRAY_ADJUSTED
            beta_adjusted = beta * DEFINES.SDSS_TO_ORBRAY_GEAR_RATIO * DEFINES.PROTO_21_ORBRAY_ADJUSTED
            log.debug(f"Set alpha from {alpha} relative adjusted to {alpha_adjusted}, beta from {beta} relative adjusted to {beta_adjusted}")
            return fn(self,alpha_adjusted, beta_adjusted)
        elif manufacturer and manufacturer.lower() == "mps_swapped_motors":
            if self._canid == 23:
                alpha_adjusted = alpha * DEFINES.ORBRAY_TO_MAXON_GEAR_RATIO
                beta_adjusted = beta * DEFINES.ORBRAY_TO_MAXON_GEAR_RATIO
                log.debug(f"Set alpha from {alpha} relative adjusted to {alpha_adjusted}, beta from {beta} relative adjusted to {beta_adjusted}")
                return fn(self, alpha_adjusted, beta_adjusted)
            elif self._canid == 25 or self._canid == 26:
                alpha_adjusted = alpha * DEFINES.MAXON_TO_ORBRAY_GEAR_RATIO
                beta_adjusted = beta * DEFINES.MAXON_TO_ORBRAY_GEAR_RATIO
                log.debug(f"Set alpha from {alpha} relative adjusted to {alpha_adjusted}, beta from {beta} relative adjusted to {beta_adjusted}")
                return fn(self, alpha_adjusted, beta_adjusted)     
        else:
            return fn(self,alpha, beta)
    return wrapper

def manufacturer_adjust_relative(fn):
    """
    Wraps a goto_relative(alpha,beta) so that if the
    manufacturer is 'Orbray' (trillium mechanism), beta is adjusted to (beta - alpha).
    The command is also adjusted to the gear ratio of the Orbray positioners.
    """
    @wraps(fn)
    def wrapper(self,alpha, beta, *, manufacturer=None):
        manufacturer = getattr(DEFINES, "MANUFACTURER", None)
        #here we use a global variable for backwards compatibility reasons
        if manufacturer and manufacturer.lower() == "orbray":
            beta_adjusted = (beta - alpha) * DEFINES.SDSS_TO_ORBRAY_GEAR_RATIO * DEFINES.PROTO_21_ORBRAY_ADJUSTED
            alpha_adjusted = alpha * DEFINES.SDSS_TO_ORBRAY_GEAR_RATIO * DEFINES.PROTO_21_ORBRAY_ADJUSTED
            log.debug(f"Moving alpha to {alpha} relative adjusted to {alpha_adjusted}, beta to {beta} relative adjusted to {beta_adjusted}")
            return fn(self,alpha_adjusted, beta_adjusted)
        elif manufacturer and manufacturer.lower() == "mps_swapped_motors":
            #WARNING: workaround that supposes that posid = can id
            if self._canid == 23:
                alpha_adjusted = alpha * DEFINES.ORBRAY_TO_MAXON_GEAR_RATIO
                beta_adjusted = beta * DEFINES.ORBRAY_TO_MAXON_GEAR_RATIO
                log.debug(f"Set alpha from {alpha} relative adjusted to {alpha_adjusted}, beta from {beta} relative adjusted to {beta_adjusted}")
                return fn(self, alpha_adjusted, beta_adjusted)
            elif self._canid == 25 or self._canid == 26:
                alpha_adjusted = alpha * DEFINES.MAXON_TO_ORBRAY_GEAR_RATIO
                beta_adjusted = beta * DEFINES.MAXON_TO_ORBRAY_GEAR_RATIO
                log.debug(f"Set alpha from {alpha} relative adjusted to {alpha_adjusted}, beta from {beta} relative adjusted to {beta_adjusted}")
                return fn(self, alpha_adjusted, beta_adjusted)
        else:
            return fn(self,alpha, beta)
    return wrapper

def manufacturer_adjust_absolute(fn):
    """
    Wraps a goto_absolute(self, alpha, beta) so that if the
    manufacturer is 'Orbray' (trillium mechanism), beta is adjusted based
    on the relative alpha movement.

    This decorator retrieves the current position to compute the relative
    alpha movement (delta_alpha) and adjusts the target beta accordingly.
    The adjustment logic is equivalent to: `new_beta = beta - abs(delta_alpha)`.
    """
    @wraps(fn)
    def wrapper(self, alpha, beta, *args, **kwargs):
        # for backwards compatibility, manufacturer is a global in DEFINES
        # Using getattr for safety in case DEFINES doesn't have it.
        manufacturer = getattr(DEFINES, "MANUFACTURER", None)

        adjusted_beta = beta
        if manufacturer and manufacturer.lower() == "orbray":
            # The 'self' is refering to a Positioner instance.
            current_position = self.get_position()

            if current_position is not None:
                current_alpha, _ = current_position
                
                # Calculate the relative alpha movement
                delta_alpha = alpha - current_alpha
                
                # Adjust beta based on the magnitude of the alpha move.
                beta_adjusted = (beta - delta_alpha) * DEFINES.SDSS_TO_ORBRAY_GEAR_RATIO * DEFINES.PROTO_21_ORBRAY_ADJUSTED
                alpha_adjusted = alpha * DEFINES.SDSS_TO_ORBRAY_GEAR_RATIO * DEFINES.PROTO_21_ORBRAY_ADJUSTED

            else:
                # Could not get current position, cannot adjust.
                # The positioner methods already log errors, so a specific 
                # warning for the adjustment failing is useful.
                log.warning("Could not get current position for ID %s. "
                            "Unable to perform manufacturer-specific adjustment for absolute move.",
                            getattr(self, '_canid', 'N/A'))

            log.debug(f"Moving alpha to {alpha} adjusted to {alpha_adjusted}, beta to {beta} adjusted to {beta_adjusted}")
            return fn(self, alpha_adjusted, beta_adjusted, *args, **kwargs)
        
        elif manufacturer and manufacturer.lower() == "mps_swapped_motors":
            #WARNING: workaround that supposes that posid = can id
            if self._canid == 23:
                alpha_adjusted = alpha * DEFINES.ORBRAY_TO_MAXON_GEAR_RATIO
                beta_adjusted = beta * DEFINES.ORBRAY_TO_MAXON_GEAR_RATIO
                log.debug(f"Set alpha from {alpha} relative adjusted to {alpha_adjusted}, beta from {beta} relative adjusted to {beta_adjusted}")
                return fn(self, alpha_adjusted, beta_adjusted)
            elif self._canid == 25 or self._canid == 26:
                alpha_adjusted = alpha * DEFINES.MAXON_TO_ORBRAY_GEAR_RATIO
                beta_adjusted = beta * DEFINES.MAXON_TO_ORBRAY_GEAR_RATIO
                log.debug(f"Set alpha from {alpha} relative adjusted to {alpha_adjusted}, beta from {beta} relative adjusted to {beta_adjusted}")
                return fn(self, alpha_adjusted, beta_adjusted)
        else:
            return fn(self, alpha, beta, *args, **kwargs)
    return wrapper
