SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='TRADITIONAL';

CREATE SCHEMA IF NOT EXISTS `davdav` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci ;
USE `davdav` ;

-- -----------------------------------------------------
-- Table `davdav`.`thumbnail`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `davdav`.`thumbnail` ;

CREATE  TABLE IF NOT EXISTS `davdav`.`thumbnail` (
  `id` INT NOT NULL AUTO_INCREMENT ,
  `original` VARCHAR(255) NOT NULL ,
  `thumbnail` VARCHAR(255) NOT NULL ,
  `created_at` DATETIME NOT NULL ,
  `updated_at` DATETIME NOT NULL ,
  `enable` TINYINT(1) NOT NULL ,
  PRIMARY KEY (`id`) ,
  UNIQUE INDEX `id_UNIQUE` (`id` ASC) )
ENGINE = InnoDB;



SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
